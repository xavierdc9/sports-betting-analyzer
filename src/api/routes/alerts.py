"""API routes for alerts."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import AlertOut
from src.database import get_db
from src.models.alert import Alert

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=List[AlertOut])
async def list_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by type (arbitrage, value_bet, line_movement)"),
    unread_only: bool = Query(False, description="Only return unread alerts"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List alerts with optional filters."""
    query = select(Alert)
    if alert_type is not None:
        query = query.where(Alert.alert_type == alert_type)
    if unread_only:
        query = query.where(Alert.is_read == False)  # noqa: E712
    query = query.order_by(Alert.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.patch("/{alert_id}/read")
async def mark_alert_read(
    alert_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Mark an alert as read."""
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if alert is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.is_read = True
    await db.flush()
    return {"status": "ok"}


@router.post("/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
):
    """Mark all unread alerts as read."""
    await db.execute(
        update(Alert).where(Alert.is_read == False).values(is_read=True)  # noqa: E712
    )
    await db.flush()
    return {"status": "ok"}
