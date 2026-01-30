"""API routes for manual scraper triggers."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.analysis.alert_generator import generate_arb_alerts, generate_value_alerts
from src.database import get_db
from src.scraper.service import ScraperService

router = APIRouter(prefix="/api/scraper", tags=["scraper"])


@router.post("/scrape")
async def trigger_scrape(
    sport_key: str = Query(..., description="Sport key to scrape (e.g. americanfootball_nfl)"),
    regions: str = Query("us", description="Comma-separated bookmaker regions"),
    markets: str = Query("h2h,spreads,totals", description="Comma-separated market types"),
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger a scrape for a specific sport."""
    service = ScraperService()
    count = await service.scrape_odds(
        db, sport_key=sport_key, regions=regions, markets=markets,
    )
    return {"status": "ok", "odds_records_created": count}


@router.post("/analyze")
async def trigger_analysis(
    db: AsyncSession = Depends(get_db),
):
    """Manually trigger analysis on current odds data."""
    arb_alerts = await generate_arb_alerts(db)
    value_alerts = await generate_value_alerts(db)
    return {
        "status": "ok",
        "arbitrage_alerts": len(arb_alerts),
        "value_bet_alerts": len(value_alerts),
    }
