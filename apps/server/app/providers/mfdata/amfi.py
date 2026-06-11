"""AMFI NAV provider. Latest NAVs from NAVAll.txt, history from the AMFI report URL."""

from __future__ import annotations

import httpx

from app.core.errors import NotFoundError, ProviderUnavailableError
from app.providers.mfdata.base import MfDataProvider, NavPoint, SchemeNav

NAV_ALL_URL = "https://www.amfiindia.com/spages/NAVAll.txt"
NAV_HISTORY_URL = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"


def parse_nav_all(text: str) -> dict[str, SchemeNav]:
    """Parse the semicolon-delimited AMFI NAVAll feed keyed by scheme code."""
    schemes: dict[str, SchemeNav] = {}
    for line in text.splitlines():
        parts = line.split(";")
        if len(parts) < 6 or not parts[0].strip().isdigit():
            continue
        code, name = parts[0].strip(), parts[3].strip()
        nav, date = parts[4].strip(), parts[5].strip()
        try:
            value = float(nav)
        except ValueError:
            continue
        schemes[code] = SchemeNav(scheme_code=code, scheme_name=name, nav=value, date=date)
    return schemes


def parse_nav_history(text: str) -> list[NavPoint]:
    points: list[NavPoint] = []
    for line in text.splitlines():
        parts = line.split(";")
        if len(parts) < 8 or not parts[0].strip().isdigit():
            continue
        try:
            points.append(NavPoint(date=parts[7].strip(), nav=float(parts[4].strip())))
        except ValueError:
            continue
    return points


class AmfiMfData(MfDataProvider):
    def __init__(self, timeout_seconds: float = 10.0):
        self._timeout = timeout_seconds

    async def _get(self, url: str, params: dict | None = None) -> str:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.text
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError("mfdata", str(exc)) from exc

    async def latest_nav(self, scheme_code: str) -> SchemeNav:
        schemes = parse_nav_all(await self._get(NAV_ALL_URL))
        if scheme_code not in schemes:
            raise NotFoundError(f"AMFI scheme '{scheme_code}' not found")
        return schemes[scheme_code]

    async def nav_history(self, scheme_code: str, from_date: str, to_date: str) -> list[NavPoint]:
        text = await self._get(
            NAV_HISTORY_URL,
            params={"scm": scheme_code, "frmdt": from_date, "todt": to_date},
        )
        return parse_nav_history(text)
