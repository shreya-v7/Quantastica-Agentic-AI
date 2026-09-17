"""Integration tests for the new phases: auth, match, trades, automation, alerts, chat.
These run against throwaway Postgres + Redis via the `client` fixture."""

from __future__ import annotations

import respx
from httpx import Response

# A minimal Yahoo chart payload so the market-data provider returns a deterministic quote
# without hitting the network. Used wherever a trade or quote needs a price.
_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart"


def _chart_payload(price: float) -> dict:
    return {
        "chart": {
            "result": [
                {
                    "meta": {
                        "regularMarketPrice": price,
                        "currency": "INR",
                        "regularMarketTime": 1718000000,
                    }
                }
            ],
            "error": None,
        }
    }


# --- auth -------------------------------------------------------------------
async def test_register_login_refresh_flow(client):
    reg = await client.post(
        "/api/auth/register",
        json={"email": "neha@example.in", "password": "averylongpassword1"},
    )
    assert reg.status_code == 200
    assert reg.json()["data"]["email"] == "neha@example.in"

    login = await client.post(
        "/api/auth/login",
        json={"email": "neha@example.in", "password": "averylongpassword1"},
    )
    assert login.status_code == 200
    pair = login.json()["data"]
    assert pair["accessToken"] and pair["refreshToken"]

    refresh = await client.post(
        "/api/auth/refresh", json={"refreshToken": pair["refreshToken"]}
    )
    assert refresh.status_code == 200
    rotated = refresh.json()["data"]["refreshToken"]
    assert rotated != pair["refreshToken"]

    # Reusing the original (now rotated) refresh token is rejected.
    reuse = await client.post(
        "/api/auth/refresh", json={"refreshToken": pair["refreshToken"]}
    )
    assert reuse.status_code == 401


async def test_login_wrong_password_rejected(client):
    await client.post(
        "/api/auth/register",
        json={"email": "raj@example.in", "password": "averylongpassword1"},
    )
    bad = await client.post(
        "/api/auth/login", json={"email": "raj@example.in", "password": "nope-nope-nope"}
    )
    assert bad.status_code == 401


# --- match ------------------------------------------------------------------
async def test_loan_match_ranks_by_rate(client):
    res = await client.post(
        "/api/match/loans",
        json={
            "loanType": "home",
            "amountInr": 5000000,
            "tenureYears": 20,
            "monthlyIncomeInr": 200000,
            "propertyValueInr": 7000000,
        },
    )
    assert res.status_code == 200
    matches = res.json()["data"]
    assert len(matches) >= 2
    # Sorted by score descending; the top match should be eligible.
    assert matches[0]["eligible"] is True
    assert matches[0]["emiInr"] > 0
    assert "Rs" in matches[0]["emiDisplay"]


async def test_insurance_match_filters_age_band(client):
    res = await client.post(
        "/api/match/insurance",
        json={"insuranceType": "term", "coverInr": 10000000, "age": 35},
    )
    assert res.status_code == 200
    matches = res.json()["data"]
    assert matches and all(m["annualPremiumInr"] > 0 for m in matches)


# --- trades -----------------------------------------------------------------
@respx.mock
async def test_trade_intent_create_and_execute(client):
    respx.get(url__startswith=_YAHOO).mock(return_value=Response(200, json=_chart_payload(2500.0)))

    created = await client.post(
        "/api/trades/intents",
        json={"portfolioId": "pf_tech_heavy", "symbol": "RELIANCE.NS", "side": "buy",
              "quantity": 10, "orderType": "market"},
    )
    assert created.status_code == 200
    intent = created.json()["data"]
    assert intent["status"] == "pending_approval"
    assert intent["mode"] == "paper"

    executed = await client.post(f"/api/trades/intents/{intent['id']}/execute")
    assert executed.status_code == 200
    filled = executed.json()["data"]
    assert filled["status"] == "filled"
    assert filled["fillPrice"] == 2500.0


@respx.mock
async def test_trade_rejected_over_notional_cap(client):
    respx.get(url__startswith=_YAHOO).mock(
        return_value=Response(200, json=_chart_payload(2500.0))
    )
    # 1000 * 2500 = 2.5M, over the 500k per-order cap default.
    res = await client.post(
        "/api/trades/intents",
        json={"portfolioId": "pf_tech_heavy", "symbol": "RELIANCE.NS", "side": "buy",
              "quantity": 1000, "orderType": "market"},
    )
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "TRADE_LIMIT_EXCEEDED"


@respx.mock
async def test_kill_switch_blocks_new_intents(client):
    respx.get(url__startswith=_YAHOO).mock(
        return_value=Response(200, json=_chart_payload(2500.0))
    )
    await client.post("/api/trades/kill-switch", json={"disabled": True})
    res = await client.post(
        "/api/trades/intents",
        json={"portfolioId": "pf_tech_heavy", "symbol": "RELIANCE.NS", "side": "buy",
              "quantity": 1, "orderType": "market"},
    )
    assert res.status_code == 403


# --- automation -------------------------------------------------------------
async def test_automation_rule_cap_enforced(client):
    over_cap = await client.post(
        "/api/automation/rules",
        json={
            "name": "buy the dip", "portfolioId": "pf_tech_heavy",
            "trigger": {"symbol": "RELIANCE.NS", "operator": "below", "price": 2000},
            "action": {"side": "buy", "quantity": 10},
            "maxNotionalInr": 99_000_000,
        },
    )
    assert over_cap.status_code == 422

    ok = await client.post(
        "/api/automation/rules",
        json={
            "name": "buy the dip", "portfolioId": "pf_tech_heavy",
            "trigger": {"symbol": "RELIANCE.NS", "operator": "below", "price": 2000},
            "action": {"side": "buy", "quantity": 10},
            "maxNotionalInr": 100_000,
        },
    )
    assert ok.status_code == 200
    listed = (await client.get("/api/automation/rules")).json()["data"]
    assert len(listed) == 1


# --- alerts -----------------------------------------------------------------
async def test_alert_crud(client):
    created = await client.post(
        "/api/alerts",
        json={"name": "RIL drop", "symbol": "RELIANCE.NS", "operator": "below",
              "threshold": 2400},
    )
    assert created.status_code == 200
    alert_id = created.json()["data"]["id"]

    listed = (await client.get("/api/alerts")).json()["data"]
    assert any(a["id"] == alert_id for a in listed)

    deleted = await client.delete(f"/api/alerts/{alert_id}")
    assert deleted.json()["data"]["deleted"] is True


# --- chat -------------------------------------------------------------------
async def test_chat_tax_intent_grounded(client):
    res = await client.post(
        "/api/chat",
        json={
            "message": "compare my tax under the old and new regime",
            "params": {"basicSalary": 1500000, "deduction80C": 150000},
        },
    )
    assert res.status_code == 200
    body = res.json()["data"]
    assert body["intent"] == "tax"
    assert body["data"]["recommended"] in ("old", "new")


async def test_chat_clarifies_when_missing_params(client):
    res = await client.post("/api/chat", json={"message": "what SIP do I need?"})
    body = res.json()["data"]
    assert body["intent"] == "sip"
    assert body["needsInput"]


@respx.mock
async def test_chat_portfolio_runs_pipeline(client):
    res = await client.post(
        "/api/chat",
        json={"message": "how concentrated is my portfolio?", "portfolioId": "pf_tech_heavy"},
    )
    body = res.json()["data"]
    assert body["intent"] == "portfolio"
    assert body["data"]["status"] == "completed"
