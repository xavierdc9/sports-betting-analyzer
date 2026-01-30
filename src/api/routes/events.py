"""API routes for events."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import EventOut
from src.database import get_db
from src.models.event import Event

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=List[EventOut])
async def list_events(
    sport_id: Optional[UUID] = Query(None, description="Filter by sport"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List events with optional filters."""
    query = select(Event)
    if sport_id is not None:
        query = query.where(Event.sport_id == sport_id)
    if completed is not None:
        query = query.where(Event.completed == completed)
    query = query.order_by(Event.commence_time.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{event_id}", response_model=EventOut)
async def get_event(
    event_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single event by ID."""
    result = await db.execute(select(Event).where(Event.id == event_id))
    event = result.scalar_one_or_none()
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
