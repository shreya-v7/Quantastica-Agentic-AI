"""Pure-function tests for automation firing decisions and document chunking. No DB."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.core.config import Settings
from app.providers.marketdata.base import Quote
from app.services.automation_service import fire_decision, trigger_met
from app.services.document_service import chunk_text
from app.workers.runner import alert_met


def _quote(price: float, prev: float | None = None) -> Quote:
    return Quote(symbol="RELIANCE.NS", price=price, currency="INR",
                 timestamp="2026-06-18T00:00:00+00:00", previous_close=prev)


def test_alert_met_price_above_and_below():
    assert alert_met("price", "above", _quote(2600), 2500) is True
    assert alert_met("price", "above", _quote(2400), 2500) is False
    assert alert_met("price", "below", _quote(2400), 2500) is True


def test_alert_met_percent_move():
    # 6% up move clears a 5% threshold; 3% does not.
    assert alert_met("percent_move", "above", _quote(2120, prev=2000), 0.05) is True
    assert alert_met("percent_move", "above", _quote(2060, prev=2000), 0.05) is False
    # Downward moves count by absolute magnitude.
    assert alert_met("percent_move", "above", _quote(1880, prev=2000), 0.05) is True


def test_alert_met_percent_move_without_previous_close_is_false():
    assert alert_met("percent_move", "above", _quote(2120, prev=None), 0.05) is False


class _Rule:
    """Lightweight stand-in for AutomationRuleRow (only the attributes used)."""

    def __init__(self, **kw):
        self.enabled = kw.get("enabled", True)
        self.trigger = kw.get("trigger", {"symbol": "RELIANCE.NS", "operator": "below", "price": 2800})
        self.action = kw.get("action", {"side": "buy", "quantity": 10})
        self.max_notional_inr = kw.get("max_notional_inr", 100_000)
        self.cooldown_seconds = kw.get("cooldown_seconds", 3600)
        self.executions_today = kw.get("executions_today", 0)
        self.day_notional_inr = kw.get("day_notional_inr", 0.0)
        self.counter_date = kw.get("counter_date", datetime.now(UTC).date().isoformat())
        self.last_fired_at = kw.get("last_fired_at")


def _settings() -> Settings:
    return Settings(
        _env_file=None,
        app_env="dev",
        platform="local",
        anthropic_api_key="x",
        automation_hard_max_notional_inr=200_000,
        automation_hard_max_executions_per_day=20,
        automation_hard_max_daily_notional_inr=1_000_000,
    )


def test_trigger_met_directions():
    assert trigger_met("below", 2700, 2800) is True
    assert trigger_met("below", 2900, 2800) is False
    assert trigger_met("above", 2900, 2800) is True


def test_fires_when_condition_met():
    should, reason = fire_decision(_Rule(), 2700, datetime.now(UTC), True, _settings())
    assert should is True
    assert reason == "ok"


def test_skips_when_user_disabled():
    should, reason = fire_decision(_Rule(), 2700, datetime.now(UTC), False, _settings())
    assert should is False
    assert "disabled" in reason


def test_skips_within_cooldown():
    rule = _Rule(last_fired_at=datetime.now(UTC) - timedelta(minutes=5))
    should, reason = fire_decision(rule, 2700, datetime.now(UTC), True, _settings())
    assert should is False
    assert reason == "within cooldown"


def test_skips_over_hard_notional_cap():
    rule = _Rule(action={"side": "buy", "quantity": 1000}, max_notional_inr=200_000)
    # 1000 * 2700 = 2.7M, over the 200k hard cap.
    should, reason = fire_decision(rule, 2700, datetime.now(UTC), True, _settings())
    assert should is False
    assert "hard cap" in reason


def test_skips_over_daily_execution_cap():
    rule = _Rule(executions_today=20)
    should, reason = fire_decision(rule, 2700, datetime.now(UTC), True, _settings())
    assert should is False
    assert "execution cap" in reason


def test_skips_over_daily_notional_cap():
    rule = _Rule(day_notional_inr=999_000)
    should, reason = fire_decision(rule, 2700, datetime.now(UTC), True, _settings())
    assert should is False
    assert "daily notional" in reason


def test_chunk_text_overlaps_and_covers():
    text = "word " * 500
    chunks = chunk_text(text, size=200, overlap=50)
    assert len(chunks) > 1
    assert all(len(c) <= 200 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("   ") == []
