"""Value bet detection using a sharp bookmaker as reference."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Bookmakers considered "sharp" (efficient markets)
SHARP_BOOKMAKERS = {"pinnacle", "betfair_ex_uk", "betfair_ex_eu", "betfair_ex_au"}


@dataclass
class ValueBet:
    """A detected value bet opportunity."""

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


def _remove_overround(
    sharp_prices: Dict[str, Decimal],
) -> Dict[str, Decimal]:
    """Convert sharp bookmaker odds to true probabilities by removing the overround.

    The overround (vig/juice) is the amount by which implied probabilities
    exceed 100%. We distribute it proportionally.
    """
    if not sharp_prices:
        return {}

    implied_probs = {
        name: Decimal("1") / price for name, price in sharp_prices.items()
    }
    overround = sum(implied_probs.values())

    if overround <= 0:
        return {}

    return {
        name: prob / overround for name, prob in implied_probs.items()
    }


def find_value_bets(
    event_id: str,
    home_team: str,
    away_team: str,
    market_type: str,
    odds_by_bookmaker: Dict[str, Dict[str, Decimal]],
    bookmaker_names: Dict[str, str],
    min_edge_pct: Decimal = Decimal("1.0"),
    sharp_books: Optional[set] = None,
) -> List[ValueBet]:
    """Find value bets by comparing soft bookmaker odds to sharp lines.

    Args:
        event_id: The event identifier.
        home_team: Home team name.
        away_team: Away team name.
        market_type: Market type.
        odds_by_bookmaker: Maps bookmaker_key -> {outcome_name: price}.
        bookmaker_names: Maps bookmaker_key -> display name.
        min_edge_pct: Minimum edge percentage to report.
        sharp_books: Set of sharp bookmaker keys (defaults to SHARP_BOOKMAKERS).

    Returns:
        List of ValueBet opportunities.
    """
    sharp_books = sharp_books or SHARP_BOOKMAKERS

    # Find sharp bookmaker odds
    sharp_key = None
    sharp_prices: Dict[str, Decimal] = {}
    for bm_key in sharp_books:
        if bm_key in odds_by_bookmaker:
            sharp_key = bm_key
            sharp_prices = odds_by_bookmaker[bm_key]
            break

    if not sharp_key or not sharp_prices:
        return []

    # Calculate true probabilities
    true_probs = _remove_overround(sharp_prices)
    if not true_probs:
        return []

    value_bets = []

    for bm_key, outcomes in odds_by_bookmaker.items():
        if bm_key in sharp_books:
            continue

        for outcome_name, price in outcomes.items():
            if outcome_name not in true_probs:
                continue

            true_prob = true_probs[outcome_name]
            fair_odds = Decimal("1") / true_prob

            if price > fair_odds:
                implied_prob = Decimal("1") / price
                edge_pct = ((true_prob - implied_prob) / implied_prob) * Decimal("100")
                ev = (true_prob * (price - Decimal("1"))) - (Decimal("1") - true_prob)

                if edge_pct >= min_edge_pct:
                    value_bets.append(
                        ValueBet(
                            event_id=event_id,
                            home_team=home_team,
                            away_team=away_team,
                            market_type=market_type,
                            outcome_name=outcome_name,
                            bookmaker_key=bm_key,
                            bookmaker_name=bookmaker_names.get(bm_key, bm_key),
                            odds=price,
                            sharp_odds=sharp_prices[outcome_name],
                            sharp_bookmaker=sharp_key,
                            true_probability=round(true_prob, 6),
                            edge_pct=round(edge_pct, 4),
                            expected_value=round(ev, 6),
                        )
                    )

    logger.debug(
        "Found %d value bets for event %s market %s",
        len(value_bets),
        event_id,
        market_type,
    )
    return value_bets
