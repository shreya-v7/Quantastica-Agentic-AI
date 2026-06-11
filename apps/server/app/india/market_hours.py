"""NSE/BSE market hours and holiday calendar, all in IST.

Regular session: 9:15 to 15:30 IST, Monday to Friday, excluding exchange holidays.
Holiday calendars are versioned data files per year under app/india/holidays/.
"""

from __future__ import annotations

import json
from datetime import date, datetime, time, timedelta
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)

_HOLIDAY_DIR = Path(__file__).parent / "holidays"


class HolidayCalendarMissingError(Exception):
    """Raised when no holiday calendar file exists for the requested year."""

    def __init__(self, year: int):
        super().__init__(
            f"No NSE holiday calendar for {year}. "
            f"Add app/india/holidays/nse_{year}.json."
        )


@lru_cache
def holidays_for(year: int) -> frozenset[date]:
    path = _HOLIDAY_DIR / f"nse_{year}.json"
    if not path.exists():
        raise HolidayCalendarMissingError(year)
    payload = json.loads(path.read_text())
    return frozenset(date.fromisoformat(d) for d in payload["holidays"])


def now_ist() -> datetime:
    return datetime.now(IST)


def is_trading_day(day: date) -> bool:
    if day.weekday() >= 5:
        return False
    return day not in holidays_for(day.year)


def is_market_open(at: datetime | None = None) -> bool:
    moment = (at or now_ist()).astimezone(IST)
    if not is_trading_day(moment.date()):
        return False
    return MARKET_OPEN <= moment.time() <= MARKET_CLOSE


def next_market_open(after: datetime | None = None) -> datetime:
    moment = (after or now_ist()).astimezone(IST)
    candidate = moment.date()
    if moment.time() >= MARKET_OPEN or not is_trading_day(candidate):
        candidate += timedelta(days=1)
    while not is_trading_day(candidate):
        candidate += timedelta(days=1)
    return datetime.combine(candidate, MARKET_OPEN, tzinfo=IST)
