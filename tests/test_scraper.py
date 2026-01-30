"""Tests for the odds scraper service."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from src.models.bookmaker import Bookmaker
from src.models.event import Event
from src.models.odds import OddsRecord
from src.models.sport import Sport
from src.scraper.odds_api import OddsApiClient
from src.scraper.schemas import (
    BookmakerResponse,
    EventOddsResponse,
    MarketResponse,
    OutcomeResponse,
    SportResponse,
)
from src.scraper.service import ScraperService


# --- Fixtures ---

SAMPLE_SPORTS = [
    SportResponse(
        key="americanfootball_nfl",
        group="American Football",
        title="NFL",
        description="US Football",
        active=True,
        has_outrights=False,
    ),
    SportResponse(
        key="basketball_nba",
        group="Basketball",
        title="NBA",
        description="US Basketball",
        active=True,
        has_outrights=False,
    ),
]

SAMPLE_ODDS = [
    EventOddsResponse(
        id="event123abc",
        sport_key="americanfootball_nfl",
        sport_title="NFL",
        commence_time=datetime(2026, 2, 1, 20, 0, tzinfo=timezone.utc),
        home_team="Kansas City Chiefs",
        away_team="Philadelphia Eagles",
        bookmakers=[
            BookmakerResponse(
                key="fanduel",
                title="FanDuel",
                last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                markets=[
                    MarketResponse(
                        key="h2h",
                        last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                        outcomes=[
                            OutcomeResponse(name="Kansas City Chiefs", price=Decimal("1.65")),
                            OutcomeResponse(name="Philadelphia Eagles", price=Decimal("2.30")),
                        ],
                    ),
                    MarketResponse(
                        key="spreads",
                        last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                        outcomes=[
                            OutcomeResponse(
                                name="Kansas City Chiefs",
                                price=Decimal("1.91"),
                                point=Decimal("-3.5"),
                            ),
                            OutcomeResponse(
                                name="Philadelphia Eagles",
                                price=Decimal("1.91"),
                                point=Decimal("3.5"),
                            ),
                        ],
                    ),
                ],
            ),
            BookmakerResponse(
                key="draftkings",
                title="DraftKings",
                last_update=datetime(2026, 1, 29, 17, 55, tzinfo=timezone.utc),
                markets=[
                    MarketResponse(
                        key="h2h",
                        last_update=datetime(2026, 1, 29, 17, 55, tzinfo=timezone.utc),
                        outcomes=[
                            OutcomeResponse(name="Kansas City Chiefs", price=Decimal("1.63")),
                            OutcomeResponse(name="Philadelphia Eagles", price=Decimal("2.35")),
                        ],
                    ),
                ],
            ),
        ],
    ),
]


def _make_mock_client(
    sports: List[SportResponse] = None,
    odds: List[EventOddsResponse] = None,
) -> OddsApiClient:
    """Create a mock OddsApiClient."""
    client = OddsApiClient(api_key="test_key")
    client.get_sports = AsyncMock(return_value=sports or [])
    client.get_odds = AsyncMock(return_value=odds or [])
    return client


# --- Tests ---


async def test_sync_sports(db_session):
    """sync_sports should create Sport records from API data."""
    client = _make_mock_client(sports=SAMPLE_SPORTS)
    service = ScraperService(client=client)

    result = await service.sync_sports(db_session)
    await db_session.commit()

    assert len(result) == 2

    sports = (await db_session.execute(select(Sport))).scalars().all()
    assert len(sports) == 2

    keys = {s.key for s in sports}
    assert "americanfootball_nfl" in keys
    assert "basketball_nba" in keys


async def test_sync_sports_idempotent(db_session):
    """Running sync_sports twice should not duplicate records."""
    client = _make_mock_client(sports=SAMPLE_SPORTS)
    service = ScraperService(client=client)

    await service.sync_sports(db_session)
    await db_session.commit()

    await service.sync_sports(db_session)
    await db_session.commit()

    sports = (await db_session.execute(select(Sport))).scalars().all()
    assert len(sports) == 2


async def test_scrape_odds_creates_records(db_session):
    """scrape_odds should create Event, Bookmaker, and OddsRecord rows."""
    client = _make_mock_client(odds=SAMPLE_ODDS)
    service = ScraperService(client=client)

    count = await service.scrape_odds(
        db_session, sport_key="americanfootball_nfl"
    )
    await db_session.commit()

    # 2 h2h outcomes from FanDuel + 2 spreads from FanDuel + 2 h2h from DraftKings = 6
    assert count == 6

    events = (await db_session.execute(select(Event))).scalars().all()
    assert len(events) == 1
    assert events[0].external_id == "event123abc"
    assert events[0].home_team == "Kansas City Chiefs"
    assert events[0].away_team == "Philadelphia Eagles"

    bookmakers = (await db_session.execute(select(Bookmaker))).scalars().all()
    bm_keys = {b.key for b in bookmakers}
    assert "fanduel" in bm_keys
    assert "draftkings" in bm_keys

    odds = (await db_session.execute(select(OddsRecord))).scalars().all()
    assert len(odds) == 6


async def test_scrape_odds_appends_records(db_session):
    """Running scrape_odds twice should append (not replace) OddsRecord rows."""
    client = _make_mock_client(odds=SAMPLE_ODDS)
    service = ScraperService(client=client)

    await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    odds = (await db_session.execute(select(OddsRecord))).scalars().all()
    # 6 from first scrape + 6 from second = 12
    assert len(odds) == 12


async def test_scrape_odds_empty_response(db_session):
    """scrape_odds should handle empty API responses gracefully."""
    client = _make_mock_client(odds=[])
    service = ScraperService(client=client)

    count = await service.scrape_odds(
        db_session, sport_key="americanfootball_nfl"
    )
    assert count == 0


async def test_odds_record_has_spread_point(db_session):
    """Spread outcomes should store the point value."""
    client = _make_mock_client(odds=SAMPLE_ODDS)
    service = ScraperService(client=client)

    await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    result = await db_session.execute(
        select(OddsRecord).where(OddsRecord.market_type == "spreads")
    )
    spreads = result.scalars().all()
    assert len(spreads) == 2
    points = {r.point for r in spreads}
    assert Decimal("-3.5") in points
    assert Decimal("3.5") in points


async def test_bookmaker_exchange_detection(db_session):
    """Betfair exchange bookmakers should have is_exchange=True."""
    exchange_odds = [
        EventOddsResponse(
            id="event456",
            sport_key="soccer_epl",
            sport_title="EPL",
            commence_time=datetime(2026, 2, 5, 15, 0, tzinfo=timezone.utc),
            home_team="Arsenal",
            away_team="Chelsea",
            bookmakers=[
                BookmakerResponse(
                    key="betfair_ex_uk",
                    title="Betfair Exchange",
                    last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                    markets=[
                        MarketResponse(
                            key="h2h",
                            last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                            outcomes=[
                                OutcomeResponse(name="Arsenal", price=Decimal("1.80")),
                                OutcomeResponse(name="Chelsea", price=Decimal("4.50")),
                                OutcomeResponse(name="Draw", price=Decimal("3.60")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]
    client = _make_mock_client(odds=exchange_odds)
    service = ScraperService(client=client)

    await service.scrape_odds(db_session, sport_key="soccer_epl")
    await db_session.commit()

    result = await db_session.execute(
        select(Bookmaker).where(Bookmaker.key == "betfair_ex_uk")
    )
    bm = result.scalar_one()
    assert bm.is_exchange is True
