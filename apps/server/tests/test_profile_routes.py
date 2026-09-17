"""Phase A FinancialProfile integration tests, plus the Phase D profile-slice chat that
derives tax inputs from the stored profile with no explicit parameters."""

from __future__ import annotations


async def test_profile_aggregate_has_seed_data_and_net_worth(client):
    res = await client.get("/api/profile")
    assert res.status_code == 200
    profile = res.json()["data"]
    assert profile["income"]["basicSalary"] == 1800000
    assert len(profile["retirementAccounts"]) == 3
    assert len(profile["goals"]) == 2
    # Net worth blends cash + deposits + retirement + equity, less debts.
    assert profile["netWorth"]["assetsInr"] > profile["netWorth"]["liabilitiesInr"]
    assert profile["netWorth"]["netWorthDisplay"]
    # Goal progress is computed and clamped to 0..1.
    assert all(0 <= g["progress"] <= 1 for g in profile["goals"])


async def test_put_income_then_read_back(client):
    res = await client.put(
        "/api/profile/income",
        json={
            "basicSalary": 1200000,
            "hraReceived": 480000,
            "specialAllowance": 200000,
            "rentPaid": 300000,
            "metro": True,
        },
    )
    assert res.status_code == 200
    profile = (await client.get("/api/profile")).json()["data"]
    assert profile["income"]["basicSalary"] == 1200000


async def test_add_and_delete_goal(client):
    created = await client.post(
        "/api/profile/goals",
        json={"name": "Car", "targetInr": 1500000, "targetDate": "2028-01-01",
              "priority": "low", "savedInr": 300000},
    )
    assert created.status_code == 200
    goal_id = created.json()["data"]["id"]

    profile = (await client.get("/api/profile")).json()["data"]
    assert any(g["id"] == goal_id for g in profile["goals"])

    deleted = await client.delete(f"/api/profile/goals/{goal_id}")
    assert deleted.json()["data"]["deleted"] is True


async def test_delete_unknown_collection_rejected(client):
    res = await client.delete("/api/profile/not-a-thing/x123")
    assert res.status_code == 422


async def test_chat_tax_uses_profile_when_no_params(client):
    res = await client.post("/api/chat", json={"message": "compare my income tax regimes"})
    body = res.json()["data"]
    assert body["intent"] == "tax"
    # Derived from the seeded profile, not from request params.
    assert body["data"]["source"] == "profile"
    assert body["data"]["recommended"] in ("old", "new")
