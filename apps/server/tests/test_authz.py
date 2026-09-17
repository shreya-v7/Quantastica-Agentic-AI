"""Authorization suite (Phase J): query-level user scoping (IDOR) and admin role gating.

Two real users are registered and logged in; each request carries that user's bearer
token. The suite proves user B can never read or mutate user A's resources, and that the
admin endpoints reject non-admin tokens.
"""

from __future__ import annotations

import respx
from app.infra.repo.auth_repo import AuthRepository
from httpx import Response

_YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart"


def _chart(price: float) -> dict:
    return {
        "chart": {
            "result": [{"meta": {"regularMarketPrice": price, "currency": "INR",
                                  "regularMarketTime": 1718000000}}],
            "error": None,
        }
    }


async def _register_login(client, email: str) -> tuple[str, str]:
    reg = await client.post(
        "/api/auth/register", json={"email": email, "password": "averylongpassword1"}
    )
    user_id = reg.json()["data"]["id"]
    login = await client.post(
        "/api/auth/login", json={"email": email, "password": "averylongpassword1"}
    )
    return user_id, login.json()["data"]["accessToken"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def test_idor_alerts_scoped_per_user(client):
    _, token_a = await _register_login(client, "alice@example.in")
    _, token_b = await _register_login(client, "bob@example.in")

    created = await client.post(
        "/api/alerts",
        json={"name": "A alert", "symbol": "RELIANCE.NS", "operator": "below", "threshold": 2000},
        headers=_auth(token_a),
    )
    alert_id = created.json()["data"]["id"]

    # B cannot see A's alert.
    b_list = await client.get("/api/alerts", headers=_auth(token_b))
    assert b_list.json()["data"] == []

    # B's delete of A's alert does not remove it (not found in B's scope).
    b_delete = await client.delete(f"/api/alerts/{alert_id}", headers=_auth(token_b))
    assert b_delete.json()["data"]["deleted"] is True  # idempotent no-op response

    a_list = await client.get("/api/alerts", headers=_auth(token_a))
    assert any(a["id"] == alert_id for a in a_list.json()["data"])


@respx.mock
async def test_idor_order_intents_scoped(client):
    respx.get(url__startswith=_YAHOO).mock(return_value=Response(200, json=_chart(2500.0)))
    _, token_a = await _register_login(client, "carol@example.in")
    _, token_b = await _register_login(client, "dave@example.in")

    created = await client.post(
        "/api/trades/intents",
        json={"portfolioId": "pf_a", "symbol": "RELIANCE.NS", "side": "buy",
              "quantity": 1, "orderType": "market"},
        headers=_auth(token_a),
    )
    intent_id = created.json()["data"]["id"]

    # B cannot read A's intent by id.
    b_get = await client.get(f"/api/trades/intents/{intent_id}", headers=_auth(token_b))
    assert b_get.status_code == 404
    # B cannot execute A's intent.
    b_exec = await client.post(
        f"/api/trades/intents/{intent_id}/execute", headers=_auth(token_b)
    )
    assert b_exec.status_code == 404


async def test_idor_profile_goal_scoped(client):
    _, token_a = await _register_login(client, "erin@example.in")
    _, token_b = await _register_login(client, "frank@example.in")

    created = await client.post(
        "/api/profile/goals",
        json={"name": "A goal", "targetInr": 1000000, "targetDate": "2030-01-01"},
        headers=_auth(token_a),
    )
    goal_id = created.json()["data"]["id"]

    b_delete = await client.delete(f"/api/profile/goals/{goal_id}", headers=_auth(token_b))
    assert b_delete.status_code == 404

    a_profile = await client.get("/api/profile", headers=_auth(token_a))
    assert any(g["id"] == goal_id for g in a_profile.json()["data"]["goals"])


async def test_admin_routes_require_admin_role(client, container):
    user_id, token = await _register_login(client, "grace@example.in")

    # A normal user token is rejected by admin routes.
    denied = await client.get("/api/admin/users", headers=_auth(token))
    assert denied.status_code == 403

    # Promote to admin and re-login so the new role is in the token claims.
    await AuthRepository(container.session_factory).set_role(user_id, "admin")
    relogin = await client.post(
        "/api/auth/login", json={"email": "grace@example.in", "password": "averylongpassword1"}
    )
    admin_token = relogin.json()["data"]["accessToken"]

    allowed = await client.get("/api/admin/users", headers=_auth(admin_token))
    assert allowed.status_code == 200
    assert any(u["id"] == user_id for u in allowed.json()["data"])

    audit = await client.get("/api/admin/audit", headers=_auth(admin_token))
    assert audit.status_code == 200
    assert any(a["action"] == "auth.login" for a in audit.json()["data"])
