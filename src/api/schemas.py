"""Pydantic response schemas for the REST API."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel


# --- Sport ---

class SportOut(BaseModel):
    id: UUID
    key: str
    title: str
    active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Event ---

class EventOut(BaseModel):
    id: UUID
    external_id: str
    sport_id: UUID
    home_team: str
    away_team: str
    commence_time: datetime
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Bookmaker ---

class BookmakerOut(BaseModel):
    id: UUID
    key: str
    name: str
    is_exchange: bool
    active: bool

    model_config = {"from_attributes": True}


# --- Odds ---

class OddsRecordOut(BaseModel):
    id: UUID
    event_id: UUID
    bookmaker_id: UUID
    market_type: str
    outcome_name: str
    price: Decimal
    point: Optional[Decimal] = None
    scraped_at: datetime

    model_config = {"from_attributes": True}


# --- Alert ---

class AlertOut(BaseModel):
    id: UUID
    alert_type: str
    event_id: UUID
    title: str
    details: Optional[Dict[str, Any]] = None
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Arbitrage ---

class ArbOutcomeOut(BaseModel):
    outcome_name: str
    best_price: Decimal
    bookmaker_key: str
    bookmaker_name: str


class ArbOpportunityOut(BaseModel):
    event_id: str
    home_team: str
    away_team: str
    market_type: str
    outcomes: List[ArbOutcomeOut]
    profit_pct: Decimal
    total_implied_prob: Decimal


# --- Value Bet ---

class ValueBetOut(BaseModel):
    event_id: str
    home_team: str
    away_team: str
    market_type: str
    outcome_name: str
    bookmaker_key: str
    bookmaker_name: str
    odds: Decimal
    sharp_odds: Decimal
    sharp_bookmaker: str
    true_probability: Decimal
    edge_pct: Decimal
    expected_value: Decimal
