"""End-to-end integration tests exercising the full pipeline."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import List
from unittest.mock import AsyncMock

from sqlalchemy import select

from src.analysis.alert_generator import generate_arb_alerts, generate_value_alerts
from src.models.alert import Alert
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


def _build_arb_scenario() -> List[EventOddsResponse]:
    """Build odds data where an arbitrage opportunity exists."""
    return [
        EventOddsResponse(
            id="arb_event_001",
            sport_key="americanfootball_nfl",
            sport_title="NFL",
            commence_time=datetime(2026, 2, 5, 20, 0, tzinfo=timezone.utc),
            home_team="Dallas Cowboys",
            away_team="New York Giants",
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
                                OutcomeResponse(name="Dallas Cowboys", price=Decimal("2.50")),
                                OutcomeResponse(name="New York Giants", price=Decimal("1.55")),
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
                                OutcomeResponse(name="Dallas Cowboys", price=Decimal("1.60")),
                                OutcomeResponse(name="New York Giants", price=Decimal("2.40")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]


def _build_value_scenario() -> List[EventOddsResponse]:
    """Build odds data where a value bet exists vs sharp line."""
    return [
        EventOddsResponse(
            id="value_event_001",
            sport_key="basketball_nba",
            sport_title="NBA",
            commence_time=datetime(2026, 2, 5, 22, 0, tzinfo=timezone.utc),
            home_team="Boston Celtics",
            away_team="Milwaukee Bucks",
            bookmakers=[
                BookmakerResponse(
                    key="pinnacle",
                    title="Pinnacle",
                    last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                    markets=[
                        MarketResponse(
                            key="h2h",
                            last_update=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
                            outcomes=[
                                OutcomeResponse(name="Boston Celtics", price=Decimal("1.80")),
                                OutcomeResponse(name="Milwaukee Bucks", price=Decimal("2.05")),
                            ],
                        ),
                    ],
                ),
                BookmakerResponse(
                    key="bovada",
                    title="Bovada",
                    last_update=datetime(2026, 1, 29, 17, 50, tzinfo=timezone.utc),
                    markets=[
                        MarketResponse(
                            key="h2h",
                            last_update=datetime(2026, 1, 29, 17, 50, tzinfo=timezone.utc),
                            outcomes=[
                                OutcomeResponse(name="Boston Celtics", price=Decimal("1.75")),
                                OutcomeResponse(name="Milwaukee Bucks", price=Decimal("2.30")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ]


async def test_full_pipeline_scrape_to_api(client, db_session):
    """Full pipeline: scrape odds -> persist to DB -> query via API."""
    # 1. Scrape odds using mock client
    mock_client = OddsApiClient(api_key="test")
    mock_client.get_sports = AsyncMock(return_value=[
        SportResponse(
            key="americanfootball_nfl", group="American Football",
            title="NFL", description="", active=True, has_outrights=False,
        ),
    ])
    mock_client.get_odds = AsyncMock(return_value=_build_arb_scenario())

    service = ScraperService(client=mock_client)

    # Sync sports and scrape
    await service.sync_sports(db_session)
    count = await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    assert count == 4  # 2 outcomes x 2 bookmakers

    # 2. Verify data via API
    # Sports
    resp = await client.get("/api/sports")
    assert resp.status_code == 200
    sports = resp.json()
    assert len(sports) == 1
    assert sports[0]["key"] == "americanfootball_nfl"

    # Events
    resp = await client.get("/api/events")
    assert resp.status_code == 200
    events = resp.json()
    assert len(events) == 1
    assert events[0]["home_team"] == "Dallas Cowboys"

    # Odds
    event_id = events[0]["id"]
    resp = await client.get(f"/api/odds?event_id={event_id}")
    assert resp.status_code == 200
    odds = resp.json()
    assert len(odds) == 4

    # Odds history
    resp = await client.get(f"/api/odds/event/{event_id}/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


async def test_arb_alert_pipeline(db_session):
    """Pipeline: scrape arb-worthy odds -> generate alerts -> verify alerts."""
    mock_client = OddsApiClient(api_key="test")
    mock_client.get_sports = AsyncMock(return_value=[])
    mock_client.get_odds = AsyncMock(return_value=_build_arb_scenario())

    service = ScraperService(client=mock_client)
    await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    # Best odds: Cowboys @ 2.50 (FanDuel), Giants @ 2.40 (DraftKings)
    # Implied: 1/2.50 + 1/2.40 = 0.40 + 0.4167 = 0.8167 < 1 -> arb!
    alerts = await generate_arb_alerts(db_session, min_profit_pct=Decimal("0"))
    await db_session.commit()

    assert len(alerts) >= 1
    arb_alert = alerts[0]
    assert arb_alert.alert_type == "arbitrage"
    assert "Dallas" in arb_alert.title or "Giants" in arb_alert.title


async def test_value_alert_pipeline(db_session):
    """Pipeline: scrape value-bet-worthy odds -> generate alerts."""
    mock_client = OddsApiClient(api_key="test")
    mock_client.get_sports = AsyncMock(return_value=[])
    mock_client.get_odds = AsyncMock(return_value=_build_value_scenario())

    service = ScraperService(client=mock_client)
    await service.scrape_odds(db_session, sport_key="basketball_nba")
    await db_session.commit()

    # Pinnacle (sharp): Celtics 1.80, Bucks 2.05
    # Bovada (soft): Celtics 1.75, Bucks 2.30
    # Bucks @ 2.30 vs Pinnacle fair odds -> value bet
    alerts = await generate_value_alerts(db_session, min_edge_pct=Decimal("0"))
    await db_session.commit()

    value_alerts = [a for a in alerts if a.alert_type == "value_bet"]
    assert len(value_alerts) >= 1


async def test_alerts_appear_in_api(client, db_session):
    """Alerts generated from analysis should be visible in the alerts API."""
    # Scrape arb scenario
    mock_client = OddsApiClient(api_key="test")
    mock_client.get_sports = AsyncMock(return_value=[])
    mock_client.get_odds = AsyncMock(return_value=_build_arb_scenario())

    service = ScraperService(client=mock_client)
    await service.scrape_odds(db_session, sport_key="americanfootball_nfl")
    await db_session.commit()

    # Generate alerts
    await generate_arb_alerts(db_session, min_profit_pct=Decimal("0"))
    await db_session.commit()

    # Check via API
    resp = await client.get("/api/alerts?alert_type=arbitrage")
    assert resp.status_code == 200
    api_alerts = resp.json()
    assert len(api_alerts) >= 1
    assert api_alerts[0]["alert_type"] == "arbitrage"
    assert api_alerts[0]["is_read"] is False

    # Mark as read
    alert_id = api_alerts[0]["id"]
    resp = await client.patch(f"/api/alerts/{alert_id}/read")
    assert resp.status_code == 200

    # Verify unread filter
    resp = await client.get("/api/alerts?unread_only=true&alert_type=arbitrage")
    assert resp.status_code == 200
    assert len(resp.json()) == 0


async def test_polymarket_accessible(client):
    """Polymarket endpoints should work independently of backend data."""
    resp = await client.get("/api/polymarket/markets")
    assert resp.status_code == 200
    markets = resp.json()
    assert len(markets) >= 3

    # Get specific market
    market_id = markets[0]["id"]
    resp = await client.get(f"/api/polymarket/markets/{market_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == market_id
