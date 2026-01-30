"""API routes for sports."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import SportOut
from src.database import get_db
from src.models.sport import Sport

router = APIRouter(prefix="/api/sports", tags=["sports"])


@router.get("", response_model=List[SportOut])
async def list_sports(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """List all sports, optionally filtered to active only."""
    query = select(Sport)
    if active_only:
        query = query.where(Sport.active == True)  # noqa: E712
    query = query.order_by(Sport.title)
    result = await db.execute(query)
    return result.scalars().all()
