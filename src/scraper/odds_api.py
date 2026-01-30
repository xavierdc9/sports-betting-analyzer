"""Async client for The Odds API (v4)."""

from __future__ import annotations

import logging
from typing import Dict, List, Optional

import httpx

from src.config import settings
from src.scraper.schemas import EventOddsResponse, SportResponse

logger = logging.getLogger(__name__)

BASE_URL = "https://api.the-odds-api.com/v4"

DEFAULT_REGIONS = "us"
DEFAULT_MARKETS = "h2h,spreads,totals"
DEFAULT_ODDS_FORMAT = "decimal"


class OddsApiClient:
    """Async HTTP client for The Odds API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = BASE_URL,
    ):
        self.api_key = api_key or settings.the_odds_api_key
        self.base_url = base_url
        self.requests_remaining: Optional[int] = None
        self.requests_used: Optional[int] = None

    def _update_quota(self, headers: Dict[str, str]) -> None:
        """Track API quota from response headers."""
        if "x-requests-remaining" in headers:
            self.requests_remaining = int(headers["x-requests-remaining"])
        if "x-requests-used" in headers:
            self.requests_used = int(headers["x-requests-used"])
        last = headers.get("x-requests-last")
        logger.debug(
            "Odds API quota: remaining=%s, used=%s, last_cost=%s",
            self.requests_remaining,
            self.requests_used,
            last,
        )

    async def get_sports(self, include_inactive: bool = False) -> List[SportResponse]:
        """Fetch available sports. This endpoint is free (no quota cost)."""
        params = {"apiKey": self.api_key}
        if include_inactive:
            params["all"] = "true"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/sports",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            self._update_quota(dict(response.headers))

        return [SportResponse(**item) for item in response.json()]

    async def get_odds(
        self,
        sport_key: str,
        regions: str = DEFAULT_REGIONS,
        markets: str = DEFAULT_MARKETS,
        odds_format: str = DEFAULT_ODDS_FORMAT,
    ) -> List[EventOddsResponse]:
        """Fetch current odds for a sport. Costs 1 credit per region x market."""
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": markets,
            "oddsFormat": odds_format,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/sports/{sport_key}/odds",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            self._update_quota(dict(response.headers))

        return [EventOddsResponse(**item) for item in response.json()]
