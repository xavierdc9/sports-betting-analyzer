"""Pydantic schemas for Polymarket prediction market data."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class PolymarketOutcome(BaseModel):
    """An outcome in a prediction market."""

    name: str
    price: Decimal  # 0.00 to 1.00 (probability)
    volume: Decimal


class PolymarketMarket(BaseModel):
    """A Polymarket prediction market."""

    id: str
    question: str
    category: str
    end_date: datetime
    active: bool
    total_volume: Decimal
    outcomes: List[PolymarketOutcome]
    source: str = "polymarket"
    url: Optional[str] = None
