"""Tests for Polymarket mock integration."""

from __future__ import annotations

from decimal import Decimal


async def test_list_polymarket_markets(client):
    """GET /api/polymarket/markets returns mock markets."""
    response = await client.get("/api/polymarket/markets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    assert all("question" in m for m in data)
    assert all("outcomes" in m for m in data)


async def test_filter_polymarket_by_category(client):
    """GET /api/polymarket/markets?category=NFL returns only NFL markets."""
    response = await client.get("/api/polymarket/markets?category=NFL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert all(m["category"] == "NFL" for m in data)


async def test_get_polymarket_market(client):
    """GET /api/polymarket/markets/{id} returns a single market."""
    response = await client.get("/api/polymarket/markets/pm_nfl_superbowl_2026")
    assert response.status_code == 200
    data = response.json()
    assert "Super Bowl" in data["question"]
    assert len(data["outcomes"]) >= 4


async def test_polymarket_market_not_found(client):
    """GET /api/polymarket/markets/{id} returns 404 for invalid ID."""
    response = await client.get("/api/polymarket/markets/nonexistent")
    assert response.status_code == 404


async def test_polymarket_outcome_prices(client):
    """Market outcome prices should be probabilities (0-1)."""
    response = await client.get("/api/polymarket/markets/pm_nba_mvp_2026")
    assert response.status_code == 200
    data = response.json()
    for outcome in data["outcomes"]:
        price = Decimal(str(outcome["price"]))
        assert Decimal("0") < price < Decimal("1")
