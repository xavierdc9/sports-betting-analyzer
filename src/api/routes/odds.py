"""API routes for odds records."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import OddsRecordOut
from src.database import get_db
from src.models.odds import OddsRecord

router = APIRouter(prefix="/api/odds", tags=["odds"])


@router.get("", response_model=List[OddsRecordOut])
async def list_odds(
    event_id: Optional[UUID] = Query(None, description="Filter by event"),
    bookmaker_id: Optional[UUID] = Query(None, description="Filter by bookmaker"),
    market_type: Optional[str] = Query(None, description="Filter by market type (h2h, spreads, totals)"),
    latest_only: bool = Query(True, description="Only return most recent scrape per event/bookmaker/market"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List odds records with optional filters."""
    query = select(OddsRecord)
    if event_id is not None:
        query = query.where(OddsRecord.event_id == event_id)
    if bookmaker_id is not None:
        query = query.where(OddsRecord.bookmaker_id == bookmaker_id)
    if market_type is not None:
        query = query.where(OddsRecord.market_type == market_type)

    query = query.order_by(OddsRecord.scraped_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/event/{event_id}/history", response_model=List[OddsRecordOut])
async def get_odds_history(
    event_id: UUID,
    bookmaker_id: Optional[UUID] = Query(None),
    market_type: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get full odds history for an event (for line movement charts)."""
    query = select(OddsRecord).where(OddsRecord.event_id == event_id)
    if bookmaker_id is not None:
        query = query.where(OddsRecord.bookmaker_id == bookmaker_id)
    if market_type is not None:
        query = query.where(OddsRecord.market_type == market_type)
    query = query.order_by(OddsRecord.scraped_at.asc())
    result = await db.execute(query)
    return result.scalars().all()
