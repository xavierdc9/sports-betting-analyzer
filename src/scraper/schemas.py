"""Pydantic schemas for parsing The Odds API responses."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class SportResponse(BaseModel):
    """A sport from /v4/sports."""

    key: str
    group: str
    title: str
    description: str
    active: bool
    has_outrights: bool


class OutcomeResponse(BaseModel):
    """A single outcome within a market."""

    name: str
    price: Decimal
    point: Optional[Decimal] = None


class MarketResponse(BaseModel):
    """A market (h2h, spreads, totals) from a bookmaker."""

    key: str
    last_update: datetime
    outcomes: List[OutcomeResponse]


class BookmakerResponse(BaseModel):
    """A bookmaker's odds for an event."""

    key: str
    title: str
    last_update: datetime
    markets: List[MarketResponse]


class EventOddsResponse(BaseModel):
    """An event with bookmaker odds from /v4/sports/{sport}/odds."""

    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: str
    away_team: str
    bookmakers: List[BookmakerResponse]
