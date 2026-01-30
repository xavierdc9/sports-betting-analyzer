"""Mock Polymarket client providing sample prediction market data."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from src.polymarket.schemas import PolymarketMarket, PolymarketOutcome

# Sample mock data representing sports-related prediction markets
MOCK_MARKETS: List[PolymarketMarket] = [
    PolymarketMarket(
        id="pm_nfl_superbowl_2026",
        question="Who will win Super Bowl LX?",
        category="NFL",
        end_date=datetime(2026, 2, 8, 23, 59, tzinfo=timezone.utc),
        active=True,
        total_volume=Decimal("2450000"),
        outcomes=[
            PolymarketOutcome(name="Kansas City Chiefs", price=Decimal("0.28"), volume=Decimal("680000")),
            PolymarketOutcome(name="Detroit Lions", price=Decimal("0.15"), volume=Decimal("370000")),
            PolymarketOutcome(name="Philadelphia Eagles", price=Decimal("0.12"), volume=Decimal("290000")),
            PolymarketOutcome(name="Buffalo Bills", price=Decimal("0.11"), volume=Decimal("260000")),
        ],
    ),
    PolymarketMarket(
        id="pm_nba_mvp_2026",
        question="Who will win NBA MVP 2025-26?",
        category="NBA",
        end_date=datetime(2026, 6, 15, 23, 59, tzinfo=timezone.utc),
        active=True,
        total_volume=Decimal("890000"),
        outcomes=[
            PolymarketOutcome(name="Nikola Jokic", price=Decimal("0.32"), volume=Decimal("285000")),
            PolymarketOutcome(name="Luka Doncic", price=Decimal("0.22"), volume=Decimal("196000")),
            PolymarketOutcome(name="Shai Gilgeous-Alexander", price=Decimal("0.18"), volume=Decimal("160000")),
            PolymarketOutcome(name="Giannis Antetokounmpo", price=Decimal("0.10"), volume=Decimal("89000")),
        ],
    ),
    PolymarketMarket(
        id="pm_nba_champ_2026",
        question="Who will win the 2026 NBA Championship?",
        category="NBA",
        end_date=datetime(2026, 6, 20, 23, 59, tzinfo=timezone.utc),
        active=True,
        total_volume=Decimal("1750000"),
        outcomes=[
            PolymarketOutcome(name="Boston Celtics", price=Decimal("0.22"), volume=Decimal("385000")),
            PolymarketOutcome(name="Oklahoma City Thunder", price=Decimal("0.18"), volume=Decimal("315000")),
            PolymarketOutcome(name="Denver Nuggets", price=Decimal("0.12"), volume=Decimal("210000")),
            PolymarketOutcome(name="New York Knicks", price=Decimal("0.09"), volume=Decimal("157500")),
        ],
    ),
    PolymarketMarket(
        id="pm_mlb_ws_2026",
        question="Who will win the 2026 World Series?",
        category="MLB",
        end_date=datetime(2026, 10, 31, 23, 59, tzinfo=timezone.utc),
        active=True,
        total_volume=Decimal("620000"),
        outcomes=[
            PolymarketOutcome(name="Los Angeles Dodgers", price=Decimal("0.20"), volume=Decimal("124000")),
            PolymarketOutcome(name="New York Yankees", price=Decimal("0.14"), volume=Decimal("86800")),
            PolymarketOutcome(name="Atlanta Braves", price=Decimal("0.10"), volume=Decimal("62000")),
            PolymarketOutcome(name="Houston Astros", price=Decimal("0.08"), volume=Decimal("49600")),
        ],
    ),
]


class MockPolymarketClient:
    """Mock client that returns sample prediction market data."""

    async def get_markets(
        self,
        category: Optional[str] = None,
        active_only: bool = True,
    ) -> List[PolymarketMarket]:
        """Get prediction markets, optionally filtered by category."""
        markets = MOCK_MARKETS

        if category:
            markets = [m for m in markets if m.category.lower() == category.lower()]

        if active_only:
            markets = [m for m in markets if m.active]

        return markets

    async def get_market(self, market_id: str) -> Optional[PolymarketMarket]:
        """Get a single market by ID."""
        for market in MOCK_MARKETS:
            if market.id == market_id:
                return market
        return None
