"""Tests for the REST API endpoints."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.models.alert import Alert
from src.models.bookmaker import Bookmaker
from src.models.event import Event
from src.models.odds import OddsRecord
from src.models.sport import Sport


# --- Fixtures ---

async def _seed_data(db_session):
    """Insert test data into the database."""
    sport = Sport(
        id=uuid.UUID("00000000-0000-0000-0000-000000000001"),
        key="americanfootball_nfl",
        title="NFL",
        active=True,
    )
    db_session.add(sport)

    event = Event(
        id=uuid.UUID("00000000-0000-0000-0000-000000000010"),
        external_id="ext_001",
        sport_id=sport.id,
        home_team="Kansas City Chiefs",
        away_team="Philadelphia Eagles",
        commence_time=datetime(2026, 2, 1, 20, 0, tzinfo=timezone.utc),
    )
    db_session.add(event)

    bookmaker = Bookmaker(
        id=uuid.UUID("00000000-0000-0000-0000-000000000100"),
        key="fanduel",
        name="FanDuel",
    )
    db_session.add(bookmaker)

    odds = OddsRecord(
        event_id=event.id,
        bookmaker_id=bookmaker.id,
        market_type="h2h",
        outcome_name="Kansas City Chiefs",
        price=Decimal("1.65"),
        scraped_at=datetime(2026, 1, 29, 18, 0, tzinfo=timezone.utc),
    )
    db_session.add(odds)

    alert = Alert(
        id=uuid.UUID("00000000-0000-0000-0000-000000001000"),
        alert_type="arbitrage",
        event_id=event.id,
        title="Arb detected: KC vs PHI",
        details={"profit_pct": 3.2},
        is_read=False,
    )
    db_session.add(alert)

    await db_session.flush()
    return {"sport": sport, "event": event, "bookmaker": bookmaker, "odds": odds, "alert": alert}


# --- Sports ---

async def test_list_sports_empty(client):
    """GET /api/sports returns empty list when no data."""
    response = await client.get("/api/sports")
    assert response.status_code == 200
    assert response.json() == []


async def test_list_sports(client, db_session):
    """GET /api/sports returns sports."""
    await _seed_data(db_session)
    response = await client.get("/api/sports")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["key"] == "americanfootball_nfl"


# --- Events ---

async def test_list_events(client, db_session):
    """GET /api/events returns events."""
    await _seed_data(db_session)
    response = await client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["home_team"] == "Kansas City Chiefs"


async def test_get_event(client, db_session):
    """GET /api/events/{id} returns a single event."""
    await _seed_data(db_session)
    eid = "00000000-0000-0000-0000-000000000010"
    response = await client.get(f"/api/events/{eid}")
    assert response.status_code == 200
    assert response.json()["external_id"] == "ext_001"


async def test_get_event_not_found(client):
    """GET /api/events/{id} returns 404 for missing event."""
    eid = "00000000-0000-0000-0000-000000000099"
    response = await client.get(f"/api/events/{eid}")
    assert response.status_code == 404


async def test_filter_events_by_sport(client, db_session):
    """GET /api/events?sport_id= filters correctly."""
    await _seed_data(db_session)
    sid = "00000000-0000-0000-0000-000000000001"
    response = await client.get(f"/api/events?sport_id={sid}")
    assert response.status_code == 200
    assert len(response.json()) == 1

    fake_sid = "00000000-0000-0000-0000-ffffffffffff"
    response2 = await client.get(f"/api/events?sport_id={fake_sid}")
    assert response2.status_code == 200
    assert len(response2.json()) == 0


# --- Odds ---

async def test_list_odds(client, db_session):
    """GET /api/odds returns odds records."""
    await _seed_data(db_session)
    response = await client.get("/api/odds")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["market_type"] == "h2h"


async def test_odds_history(client, db_session):
    """GET /api/odds/event/{id}/history returns chronological odds."""
    await _seed_data(db_session)
    eid = "00000000-0000-0000-0000-000000000010"
    response = await client.get(f"/api/odds/event/{eid}/history")
    assert response.status_code == 200
    assert len(response.json()) == 1


# --- Alerts ---

async def test_list_alerts(client, db_session):
    """GET /api/alerts returns alerts."""
    await _seed_data(db_session)
    response = await client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["alert_type"] == "arbitrage"
    assert data[0]["is_read"] is False


async def test_mark_alert_read(client, db_session):
    """PATCH /api/alerts/{id}/read marks alert as read."""
    await _seed_data(db_session)
    aid = "00000000-0000-0000-0000-000000001000"
    response = await client.patch(f"/api/alerts/{aid}/read")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


async def test_mark_alert_read_not_found(client):
    """PATCH /api/alerts/{id}/read returns 404 for missing alert."""
    aid = "00000000-0000-0000-0000-000000009999"
    response = await client.patch(f"/api/alerts/{aid}/read")
    assert response.status_code == 404


async def test_filter_alerts_unread(client, db_session):
    """GET /api/alerts?unread_only=true filters to unread."""
    await _seed_data(db_session)
    response = await client.get("/api/alerts?unread_only=true")
    assert response.status_code == 200
    assert len(response.json()) == 1

    # Mark as read
    aid = "00000000-0000-0000-0000-000000001000"
    await client.patch(f"/api/alerts/{aid}/read")

    response2 = await client.get("/api/alerts?unread_only=true")
    assert response2.status_code == 200
    assert len(response2.json()) == 0
