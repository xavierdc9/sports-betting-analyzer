"""Arbitrage detection across bookmakers for the same event/market."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal
from itertools import product
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ArbOutcome:
    """A single outcome with the best available odds across bookmakers."""

    outcome_name: str
    best_price: Decimal
    bookmaker_key: str
    bookmaker_name: str


@dataclass
class ArbOpportunity:
    """A detected arbitrage opportunity."""

    event_id: str
    home_team: str
    away_team: str
    market_type: str
    outcomes: List[ArbOutcome]
    profit_pct: Decimal
    total_implied_prob: Decimal

    def stake_allocation(self, total_stake: Decimal = Decimal("100")) -> Dict[str, Decimal]:
        """Calculate optimal stake allocation for guaranteed profit."""
        allocations = {}
        for outcome in self.outcomes:
            implied = Decimal("1") / outcome.best_price
            stake = (implied / self.total_implied_prob) * total_stake
            allocations[outcome.outcome_name] = round(stake, 2)
        return allocations


@dataclass
class OddsSnapshot:
    """A bookmaker's odds for one outcome."""

    bookmaker_key: str
    bookmaker_name: str
    outcome_name: str
    price: Decimal
    point: Optional[Decimal] = None


def find_arbitrage(
    event_id: str,
    home_team: str,
    away_team: str,
    market_type: str,
    odds_by_outcome: Dict[str, List[OddsSnapshot]],
    min_profit_pct: Decimal = Decimal("0"),
) -> Optional[ArbOpportunity]:
    """Check if arbitrage exists for a single event/market across bookmakers.

    Args:
        event_id: The event identifier.
        home_team: Home team name.
        away_team: Away team name.
        market_type: Market type (h2h, spreads, totals).
        odds_by_outcome: Maps outcome name -> list of odds from different bookmakers.
        min_profit_pct: Minimum profit percentage to report (default 0 = any arb).

    Returns:
        ArbOpportunity if arbitrage exists, None otherwise.
    """
    if len(odds_by_outcome) < 2:
        return None

    # Find best (highest) price for each outcome
    best_outcomes: List[ArbOutcome] = []
    for outcome_name, snapshots in odds_by_outcome.items():
        if not snapshots:
            return None
        best = max(snapshots, key=lambda s: s.price)
        best_outcomes.append(
            ArbOutcome(
                outcome_name=outcome_name,
                best_price=best.price,
                bookmaker_key=best.bookmaker_key,
                bookmaker_name=best.bookmaker_name,
            )
        )

    # Calculate total implied probability
    total_implied = sum(Decimal("1") / o.best_price for o in best_outcomes)

    if total_implied < Decimal("1"):
        profit_pct = (Decimal("1") - total_implied) * Decimal("100")
        if profit_pct >= min_profit_pct:
            return ArbOpportunity(
                event_id=event_id,
                home_team=home_team,
                away_team=away_team,
                market_type=market_type,
                outcomes=best_outcomes,
                profit_pct=round(profit_pct, 4),
                total_implied_prob=round(total_implied, 6),
            )

    return None


def scan_for_arbitrage(
    events_odds: List[Dict],
    min_profit_pct: Decimal = Decimal("0"),
) -> List[ArbOpportunity]:
    """Scan a batch of events for arbitrage opportunities.

    Args:
        events_odds: List of dicts with keys:
            event_id, home_team, away_team, market_type,
            odds_by_outcome (Dict[str, List[OddsSnapshot]])
        min_profit_pct: Minimum profit threshold.

    Returns:
        List of detected ArbOpportunity objects.
    """
    opportunities = []
    for event_data in events_odds:
        result = find_arbitrage(
            event_id=event_data["event_id"],
            home_team=event_data["home_team"],
            away_team=event_data["away_team"],
            market_type=event_data["market_type"],
            odds_by_outcome=event_data["odds_by_outcome"],
            min_profit_pct=min_profit_pct,
        )
        if result is not None:
            opportunities.append(result)

    logger.info(
        "Scanned %d event-markets, found %d arbitrage opportunities",
        len(events_odds),
        len(opportunities),
    )
    return opportunities
