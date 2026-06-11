def _assert_envelope(body: dict):
    assert set(body.keys()) == {"ok", "data", "error", "meta"}
    assert set(body["meta"].keys()) == {"requestId", "version"}


async def test_health(client):
    res = await client.get("/api/health")
    assert res.status_code == 200
    body = res.json()
    _assert_envelope(body)
    assert body["ok"] is True
    assert body["data"]["status"] == "ok"
    assert res.headers["X-Request-ID"]


async def test_request_id_is_propagated(client):
    res = await client.get("/api/health", headers={"X-Request-ID": "abc123"})
    assert res.headers["X-Request-ID"] == "abc123"
    assert res.json()["meta"]["requestId"] == "abc123"


async def test_platform_ready(client):
    body = (await client.get("/api/platform")).json()
    _assert_envelope(body)
    assert body["data"]["platform"] == "local"
    assert body["data"]["ready"] is True
    assert {c["name"] for c in body["data"]["components"]} == {
        "repository",
        "llm",
        "events",
        "storage",
        "cache",
    }
    provider_names = {p["name"] for p in body["data"]["providers"]}
    assert "marketdata" in provider_names
    assert "broker_paper" in provider_names


async def test_list_portfolios(client):
    body = (await client.get("/api/portfolios")).json()
    assert body["ok"] is True
    assert len(body["data"]) == 2


async def test_portfolio_detail_and_not_found(client):
    body = (await client.get("/api/portfolios/pf_tech_heavy")).json()
    assert body["data"]["portfolio"]["id"] == "pf_tech_heavy"
    assert body["data"]["metrics"]["totalValue"] > 0
    assert body["data"]["holdings"]

    missing = await client.get("/api/portfolios/nope")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "NOT_FOUND"


async def test_run_request_validation_error(client):
    res = await client.post("/api/agents/run", json={"query": ""})
    assert res.status_code == 422
    assert res.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_agent_run_end_to_end(client):
    res = await client.post(
        "/api/agents/run",
        json={"query": "How concentrated is my AI portfolio?", "portfolioId": "pf_tech_heavy"},
    )
    assert res.status_code == 200
    run = res.json()["data"]
    assert run["status"] == "completed"
    assert run["answer"]
    run_id = run["id"]

    listed = (await client.get("/api/agents/runs?portfolioId=pf_tech_heavy")).json()["data"]
    assert any(r["id"] == run_id for r in listed)

    fetched = (await client.get(f"/api/agents/runs/{run_id}")).json()["data"]
    assert fetched["id"] == run_id

    insights = (await client.get("/api/insights?portfolioId=pf_tech_heavy")).json()["data"]
    assert insights
    assert insights[0]["metricIds"]

    exported = (await client.post(f"/api/agents/runs/{run_id}/export")).json()["data"]
    assert exported["runId"] == run_id
    assert exported["location"].endswith(".json")


async def test_get_unknown_run(client):
    res = await client.get("/api/agents/runs/nope")
    assert res.status_code == 404
    assert res.json()["error"]["code"] == "NOT_FOUND"


async def test_calculator_endpoints(client):
    tax = (
        await client.post(
            "/api/tax/compare",
            json={"basicSalary": 1500000, "deduction80C": 150000, "rentPaid": 300000,
                  "hraReceived": 400000},
        )
    ).json()["data"]
    assert tax["recommended"] in ("old", "new")
    assert "," in tax["savingDisplay"] or tax["savingDisplay"].startswith("Rs")

    sip = (
        await client.post("/api/calc/sip", json={"targetInr": 5000000, "years": 10})
    ).json()["data"]
    assert sip["monthlySip"] > 0
    assert "Rs" in sip["monthlySipDisplay"]

    sim = (
        await client.post("/api/simulate", json={"monthlySip": 10000, "years": 5})
    ).json()["data"]
    assert sim["p10"] < sim["p50"] < sim["p90"]


async def test_market_rejects_bare_symbol(client):
    res = await client.get("/api/market/RELIANCE/candles")
    assert res.status_code == 422
    assert "exchange qualified" in res.json()["error"]["message"]


async def test_seed_load_and_reset(client):
    loaded = (await client.post("/api/seed/load")).json()["data"]
    assert loaded["portfolios"] == 2
    reset = (await client.post("/api/seed/reset")).json()["data"]
    assert reset["portfolios"] == 2
