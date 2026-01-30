"""Line movement tracking and CLV (Closing Line Value) analysis."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class LineMovement:
    """A detected line movement for a specific outcome."""

    event_id: str
    home_team: str
    away_team: str
    bookmaker_key: str
    market_type: str
    outcome_name: str
    old_price: Decimal
    new_price: Decimal
    price_change: Decimal
    price_change_pct: Decimal
    old_point: Optional[Decimal]
    new_point: Optional[Decimal]
    point_change: Optional[Decimal]
    old_timestamp: datetime
    new_timestamp: datetime


@dataclass
class OddsTimestamp:
    """A price snapshot at a point in time."""

    price: Decimal
    point: Optional[Decimal]
    scraped_at: datetime


def detect_line_movements(
    event_id: str,
    home_team: str,
    away_team: str,
    bookmaker_key: str,
    market_type: str,
    outcome_name: str,
    history: List[OddsTimestamp],
    min_price_change_pct: Decimal = Decimal("2.0"),
) -> List[LineMovement]:
    """Detect significant line movements from sequential odds snapshots.

    Compares each consecutive pair of snapshots. Reports movements
    exceeding the minimum percentage threshold.

    Args:
        event_id: Event identifier.
        home_team: Home team name.
        away_team: Away team name.
        bookmaker_key: Bookmaker identifier.
        market_type: Market type.
        outcome_name: Outcome name.
        history: Chronologically ordered list of odds snapshots.
        min_price_change_pct: Minimum percentage change to report.

    Returns:
        List of LineMovement detections.
    """
    if len(history) < 2:
        return []

    # Sort by timestamp to ensure chronological order
    sorted_history = sorted(history, key=lambda h: h.scraped_at)
    movements = []

    for i in range(1, len(sorted_history)):
        old = sorted_history[i - 1]
        new = sorted_history[i]

        if old.price == 0:
            continue

        price_change = new.price - old.price
        price_change_pct = (price_change / old.price) * Decimal("100")

        point_change = None
        if old.point is not None and new.point is not None:
            point_change = new.point - old.point

        if abs(price_change_pct) >= min_price_change_pct:
            movements.append(
                LineMovement(
                    event_id=event_id,
                    home_team=home_team,
                    away_team=away_team,
                    bookmaker_key=bookmaker_key,
                    market_type=market_type,
                    outcome_name=outcome_name,
                    old_price=old.price,
                    new_price=new.price,
                    price_change=round(price_change, 4),
                    price_change_pct=round(price_change_pct, 4),
                    old_point=old.point,
                    new_point=new.point,
                    point_change=point_change,
                    old_timestamp=old.scraped_at,
                    new_timestamp=new.scraped_at,
                )
            )

    return movements


def calculate_clv(
    bet_price: Decimal,
    closing_price: Decimal,
) -> Decimal:
    """Calculate Closing Line Value.

    CLV measures whether a bet was placed at better odds than the
    final (closing) line. Positive CLV indicates a good bet.

    Returns the CLV as a percentage. Positive = beat the closing line.
    """
    if closing_price == 0:
        return Decimal("0")

    bet_implied = Decimal("1") / bet_price
    close_implied = Decimal("1") / closing_price

    clv = ((close_implied - bet_implied) / bet_implied) * Decimal("100")
    return round(clv, 4)
