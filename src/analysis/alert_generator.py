"""Generate Alert records from analysis results and persist to database."""

from __future__ import annotations

import logging
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.analysis.arbitrage import ArbOpportunity, OddsSnapshot, find_arbitrage
from src.analysis.value import ValueBet, find_value_bets
from src.models.alert import Alert
from src.models.bookmaker import Bookmaker
from src.models.event import Event
from src.models.odds import OddsRecord

logger = logging.getLogger(__name__)


async def generate_arb_alerts(
    session: AsyncSession,
    min_profit_pct: Decimal = Decimal("0.5"),
) -> List[Alert]:
    """Scan latest odds for arbitrage opportunities and create alerts."""
    # Get all active (non-completed) events
    events = (
        await session.execute(
            select(Event).where(Event.completed == False)  # noqa: E712
        )
    ).scalars().all()

    if not events:
        return []

    # Load bookmakers for name lookup
    bookmakers = (await session.execute(select(Bookmaker))).scalars().all()
    bm_map = {bm.id: bm for bm in bookmakers}

    alerts_created = []

    for event in events:
        # Get latest odds for this event (most recent scraped_at per bookmaker/market/outcome)
        odds_result = await session.execute(
            select(OddsRecord)
            .where(OddsRecord.event_id == event.id)
            .order_by(OddsRecord.scraped_at.desc())
        )
        all_odds = odds_result.scalars().all()

        # Group by market type, then by outcome, collecting bookmaker odds
        markets: Dict[str, Dict[str, List[OddsSnapshot]]] = defaultdict(
            lambda: defaultdict(list)
        )
        seen = set()

        for odds_rec in all_odds:
            key = (odds_rec.bookmaker_id, odds_rec.market_type, odds_rec.outcome_name)
            if key in seen:
                continue  # Only take latest per bookmaker/market/outcome
            seen.add(key)

            bm = bm_map.get(odds_rec.bookmaker_id)
            if bm is None:
                continue

            markets[odds_rec.market_type][odds_rec.outcome_name].append(
                OddsSnapshot(
                    bookmaker_key=bm.key,
                    bookmaker_name=bm.name,
                    outcome_name=odds_rec.outcome_name,
                    price=odds_rec.price,
                    point=odds_rec.point,
                )
            )

        for market_type, odds_by_outcome in markets.items():
            arb = find_arbitrage(
                event_id=str(event.id),
                home_team=event.home_team,
                away_team=event.away_team,
                market_type=market_type,
                odds_by_outcome=dict(odds_by_outcome),
                min_profit_pct=min_profit_pct,
            )
            if arb is not None:
                alert = Alert(
                    alert_type="arbitrage",
                    event_id=event.id,
                    title=f"Arb {arb.profit_pct}%: {event.away_team} @ {event.home_team} ({market_type})",
                    details={
                        "profit_pct": str(arb.profit_pct),
                        "market_type": market_type,
                        "outcomes": [
                            {
                                "outcome": o.outcome_name,
                                "price": str(o.best_price),
                                "bookmaker": o.bookmaker_key,
                            }
                            for o in arb.outcomes
                        ],
                    },
                )
                session.add(alert)
                alerts_created.append(alert)

    await session.flush()
    logger.info("Generated %d arbitrage alerts", len(alerts_created))
    return alerts_created


async def generate_value_alerts(
    session: AsyncSession,
    min_edge_pct: Decimal = Decimal("3.0"),
) -> List[Alert]:
    """Scan latest odds for value bets and create alerts."""
    events = (
        await session.execute(
            select(Event).where(Event.completed == False)  # noqa: E712
        )
    ).scalars().all()

    if not events:
        return []

    bookmakers = (await session.execute(select(Bookmaker))).scalars().all()
    bm_map = {bm.id: bm for bm in bookmakers}
    bm_names = {bm.key: bm.name for bm in bookmakers}

    alerts_created = []

    for event in events:
        odds_result = await session.execute(
            select(OddsRecord)
            .where(OddsRecord.event_id == event.id)
            .order_by(OddsRecord.scraped_at.desc())
        )
        all_odds = odds_result.scalars().all()

        # Group by market type, then by bookmaker
        markets: Dict[str, Dict[str, Dict[str, Decimal]]] = defaultdict(
            lambda: defaultdict(dict)
        )
        seen = set()

        for odds_rec in all_odds:
            key = (odds_rec.bookmaker_id, odds_rec.market_type, odds_rec.outcome_name)
            if key in seen:
                continue
            seen.add(key)

            bm = bm_map.get(odds_rec.bookmaker_id)
            if bm is None:
                continue
            markets[odds_rec.market_type][bm.key][odds_rec.outcome_name] = odds_rec.price

        for market_type, odds_by_bookmaker in markets.items():
            value_bets = find_value_bets(
                event_id=str(event.id),
                home_team=event.home_team,
                away_team=event.away_team,
                market_type=market_type,
                odds_by_bookmaker=dict(odds_by_bookmaker),
                bookmaker_names=bm_names,
                min_edge_pct=min_edge_pct,
            )
            for vb in value_bets:
                alert = Alert(
                    alert_type="value_bet",
                    event_id=event.id,
                    title=f"Value {vb.edge_pct}%: {vb.outcome_name} @ {vb.bookmaker_name} ({market_type})",
                    details={
                        "edge_pct": str(vb.edge_pct),
                        "odds": str(vb.odds),
                        "sharp_odds": str(vb.sharp_odds),
                        "sharp_bookmaker": vb.sharp_bookmaker,
                        "bookmaker": vb.bookmaker_key,
                        "outcome": vb.outcome_name,
                        "expected_value": str(vb.expected_value),
                    },
                )
                session.add(alert)
                alerts_created.append(alert)

    await session.flush()
    logger.info("Generated %d value bet alerts", len(alerts_created))
    return alerts_created
