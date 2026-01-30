"""API routes for Polymarket prediction markets (mock data)."""

from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from src.polymarket.mock_client import MockPolymarketClient
from src.polymarket.schemas import PolymarketMarket

router = APIRouter(prefix="/api/polymarket", tags=["polymarket"])

client = MockPolymarketClient()


@router.get("/markets", response_model=List[PolymarketMarket])
async def list_markets(
    category: Optional[str] = Query(None, description="Filter by category (NFL, NBA, MLB)"),
):
    """List available prediction markets."""
    return await client.get_markets(category=category)


@router.get("/markets/{market_id}", response_model=PolymarketMarket)
async def get_market(market_id: str):
    """Get a single prediction market by ID."""
    market = await client.get_market(market_id)
    if market is None:
        raise HTTPException(status_code=404, detail="Market not found")
    return market
