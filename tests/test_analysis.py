"""Tests for the analysis engine (arbitrage, value bets, line movement, CLV)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.analysis.arbitrage import ArbOpportunity, OddsSnapshot, find_arbitrage, scan_for_arbitrage
from src.analysis.line_movement import (
    LineMovement,
    OddsTimestamp,
    calculate_clv,
    detect_line_movements,
)
from src.analysis.value import ValueBet, find_value_bets


# --- Arbitrage tests ---


class TestArbitrage:
    def test_detects_two_way_arb(self):
        """Find arb when two bookmakers offer odds that sum to <100% implied prob."""
        odds_by_outcome = {
            "Team A": [
                OddsSnapshot("book1", "Book 1", "Team A", Decimal("2.20")),
                OddsSnapshot("book2", "Book 2", "Team A", Decimal("2.10")),
            ],
            "Team B": [
                OddsSnapshot("book1", "Book 1", "Team B", Decimal("1.80")),
                OddsSnapshot("book2", "Book 2", "Team B", Decimal("1.95")),
            ],
        }
        # Best odds: Team A @ 2.20 (book1), Team B @ 1.95 (book2)
        # Implied: 1/2.20 + 1/1.95 = 0.4545 + 0.5128 = 0.9674 < 1 -> arb
        result = find_arbitrage(
            "evt1", "Team A", "Team B", "h2h", odds_by_outcome
        )
        assert result is not None
        assert result.profit_pct > Decimal("0")
        assert result.total_implied_prob < Decimal("1")

    def test_no_arb_when_overround(self):
        """No arb when combined implied probability >= 100%."""
        odds_by_outcome = {
            "Team A": [
                OddsSnapshot("book1", "Book 1", "Team A", Decimal("1.80")),
            ],
            "Team B": [
                OddsSnapshot("book1", "Book 1", "Team B", Decimal("2.00")),
            ],
        }
        # Implied: 1/1.80 + 1/2.00 = 0.5556 + 0.5 = 1.0556 > 1
        result = find_arbitrage(
            "evt1", "Team A", "Team B", "h2h", odds_by_outcome
        )
        assert result is None

    def test_three_way_arb(self):
        """Detect arb in 3-way market (soccer)."""
        odds_by_outcome = {
            "Home": [
                OddsSnapshot("book1", "Book 1", "Home", Decimal("3.60")),
                OddsSnapshot("book2", "Book 2", "Home", Decimal("3.80")),
            ],
            "Draw": [
                OddsSnapshot("book1", "Book 1", "Draw", Decimal("4.00")),
                OddsSnapshot("book2", "Book 2", "Draw", Decimal("4.20")),
            ],
            "Away": [
                OddsSnapshot("book1", "Book 1", "Away", Decimal("2.10")),
                OddsSnapshot("book2", "Book 2", "Away", Decimal("2.25")),
            ],
        }
        # Best: Home@3.80 + Draw@4.20 + Away@2.25
        # Implied: 0.2632 + 0.2381 + 0.4444 = 0.9457 < 1 -> arb
        result = find_arbitrage(
            "evt1", "Home FC", "Away FC", "h2h", odds_by_outcome
        )
        assert result is not None
        assert len(result.outcomes) == 3

    def test_stake_allocation(self):
        """Stake allocation should sum to total stake."""
        odds_by_outcome = {
            "Team A": [
                OddsSnapshot("book1", "Book 1", "Team A", Decimal("2.20")),
            ],
            "Team B": [
                OddsSnapshot("book2", "Book 2", "Team B", Decimal("1.95")),
            ],
        }
        result = find_arbitrage(
            "evt1", "Team A", "Team B", "h2h", odds_by_outcome
        )
        assert result is not None
        stakes = result.stake_allocation(Decimal("1000"))
        total = sum(stakes.values())
        assert abs(total - Decimal("1000")) < Decimal("0.1")

    def test_scan_multiple_events(self):
        """scan_for_arbitrage processes multiple event-markets."""
        events = [
            {
                "event_id": "evt1",
                "home_team": "A",
                "away_team": "B",
                "market_type": "h2h",
                "odds_by_outcome": {
                    "A": [OddsSnapshot("b1", "B1", "A", Decimal("2.20"))],
                    "B": [OddsSnapshot("b2", "B2", "B", Decimal("1.95"))],
                },
            },
            {
                "event_id": "evt2",
                "home_team": "C",
                "away_team": "D",
                "market_type": "h2h",
                "odds_by_outcome": {
                    "C": [OddsSnapshot("b1", "B1", "C", Decimal("1.50"))],
                    "D": [OddsSnapshot("b1", "B1", "D", Decimal("2.40"))],
                },
            },
        ]
        results = scan_for_arbitrage(events)
        # Only evt1 has arb
        arb_ids = [r.event_id for r in results]
        assert "evt1" in arb_ids

    def test_min_profit_filter(self):
        """Arbs below min_profit_pct should be filtered out."""
        odds_by_outcome = {
            "Team A": [
                OddsSnapshot("book1", "Book 1", "Team A", Decimal("2.20")),
            ],
            "Team B": [
                OddsSnapshot("book2", "Book 2", "Team B", Decimal("1.95")),
            ],
        }
        result = find_arbitrage(
            "evt1", "Team A", "Team B", "h2h", odds_by_outcome,
            min_profit_pct=Decimal("10"),
        )
        assert result is None  # ~3.3% profit < 10% threshold


# --- Value bet tests ---


class TestValueBets:
    def test_detects_value_bet(self):
        """Find value when soft bookmaker offers better odds than sharp fair price."""
        odds_by_bookmaker = {
            "pinnacle": {"Team A": Decimal("2.00"), "Team B": Decimal("1.90")},
            "fanduel": {"Team A": Decimal("2.25"), "Team B": Decimal("1.70")},
        }
        bookmaker_names = {"pinnacle": "Pinnacle", "fanduel": "FanDuel"}

        results = find_value_bets(
            "evt1", "Team A", "Team B", "h2h",
            odds_by_bookmaker, bookmaker_names,
            min_edge_pct=Decimal("0"),
        )

        assert len(results) > 0
        team_a_value = [r for r in results if r.outcome_name == "Team A"]
        assert len(team_a_value) == 1
        assert team_a_value[0].bookmaker_key == "fanduel"
        assert team_a_value[0].edge_pct > Decimal("0")
        assert team_a_value[0].expected_value > Decimal("0")

    def test_no_value_when_odds_fair(self):
        """No value bets when soft odds are worse than sharp fair odds."""
        odds_by_bookmaker = {
            "pinnacle": {"Team A": Decimal("2.00"), "Team B": Decimal("1.90")},
            "fanduel": {"Team A": Decimal("1.80"), "Team B": Decimal("1.85")},
        }
        bookmaker_names = {"pinnacle": "Pinnacle", "fanduel": "FanDuel"}

        results = find_value_bets(
            "evt1", "Team A", "Team B", "h2h",
            odds_by_bookmaker, bookmaker_names,
            min_edge_pct=Decimal("0"),
        )
        assert len(results) == 0

    def test_no_sharp_bookmaker(self):
        """Returns empty when no sharp bookmaker data available."""
        odds_by_bookmaker = {
            "fanduel": {"Team A": Decimal("2.00"), "Team B": Decimal("1.90")},
            "draftkings": {"Team A": Decimal("2.05"), "Team B": Decimal("1.85")},
        }
        results = find_value_bets(
            "evt1", "Team A", "Team B", "h2h",
            odds_by_bookmaker, {},
        )
        assert len(results) == 0

    def test_min_edge_filter(self):
        """Value bets below min_edge_pct should be filtered."""
        odds_by_bookmaker = {
            "pinnacle": {"Team A": Decimal("2.00"), "Team B": Decimal("1.90")},
            "fanduel": {"Team A": Decimal("2.05"), "Team B": Decimal("1.88")},
        }
        bookmaker_names = {"pinnacle": "Pinnacle", "fanduel": "FanDuel"}

        results = find_value_bets(
            "evt1", "Team A", "Team B", "h2h",
            odds_by_bookmaker, bookmaker_names,
            min_edge_pct=Decimal("20"),  # Very high threshold
        )
        assert len(results) == 0


# --- Line movement tests ---


class TestLineMovement:
    def test_detects_significant_movement(self):
        """Detect price movement exceeding threshold."""
        history = [
            OddsTimestamp(Decimal("2.00"), None, datetime(2026, 1, 29, 10, 0, tzinfo=timezone.utc)),
            OddsTimestamp(Decimal("2.20"), None, datetime(2026, 1, 29, 12, 0, tzinfo=timezone.utc)),
        ]
        movements = detect_line_movements(
            "evt1", "A", "B", "book1", "h2h", "A",
            history, min_price_change_pct=Decimal("5"),
        )
        assert len(movements) == 1
        assert movements[0].price_change == Decimal("0.2000")
        assert movements[0].price_change_pct == Decimal("10.0000")

    def test_ignores_small_movement(self):
        """Small price changes below threshold should be ignored."""
        history = [
            OddsTimestamp(Decimal("2.00"), None, datetime(2026, 1, 29, 10, 0, tzinfo=timezone.utc)),
            OddsTimestamp(Decimal("2.01"), None, datetime(2026, 1, 29, 12, 0, tzinfo=timezone.utc)),
        ]
        movements = detect_line_movements(
            "evt1", "A", "B", "book1", "h2h", "A",
            history, min_price_change_pct=Decimal("2"),
        )
        assert len(movements) == 0

    def test_tracks_point_spread_movement(self):
        """Track spread line changes along with price."""
        history = [
            OddsTimestamp(Decimal("1.91"), Decimal("-3.5"), datetime(2026, 1, 29, 10, 0, tzinfo=timezone.utc)),
            OddsTimestamp(Decimal("1.87"), Decimal("-4.5"), datetime(2026, 1, 29, 14, 0, tzinfo=timezone.utc)),
        ]
        movements = detect_line_movements(
            "evt1", "A", "B", "book1", "spreads", "A",
            history, min_price_change_pct=Decimal("1"),
        )
        assert len(movements) == 1
        assert movements[0].point_change == Decimal("-1.0")

    def test_multiple_movements(self):
        """Detect multiple sequential movements."""
        history = [
            OddsTimestamp(Decimal("2.00"), None, datetime(2026, 1, 29, 10, 0, tzinfo=timezone.utc)),
            OddsTimestamp(Decimal("2.30"), None, datetime(2026, 1, 29, 12, 0, tzinfo=timezone.utc)),
            OddsTimestamp(Decimal("1.90"), None, datetime(2026, 1, 29, 14, 0, tzinfo=timezone.utc)),
        ]
        movements = detect_line_movements(
            "evt1", "A", "B", "book1", "h2h", "A",
            history, min_price_change_pct=Decimal("5"),
        )
        assert len(movements) == 2

    def test_single_snapshot_no_movement(self):
        """Single snapshot cannot produce line movement."""
        history = [
            OddsTimestamp(Decimal("2.00"), None, datetime(2026, 1, 29, 10, 0, tzinfo=timezone.utc)),
        ]
        movements = detect_line_movements(
            "evt1", "A", "B", "book1", "h2h", "A", history,
        )
        assert len(movements) == 0


# --- CLV tests ---


class TestCLV:
    def test_positive_clv(self):
        """Positive CLV when bet placed at better odds than closing line."""
        # Bet at 2.10, closed at 1.90 -> beat the closing line
        clv = calculate_clv(Decimal("2.10"), Decimal("1.90"))
        assert clv > Decimal("0")

    def test_negative_clv(self):
        """Negative CLV when closing line was better than bet price."""
        # Bet at 1.80, closed at 2.10 -> worse than closing
        clv = calculate_clv(Decimal("1.80"), Decimal("2.10"))
        assert clv < Decimal("0")

    def test_zero_clv(self):
        """Zero CLV when bet price equals closing price."""
        clv = calculate_clv(Decimal("2.00"), Decimal("2.00"))
        assert clv == Decimal("0")

    def test_clv_zero_closing_price(self):
        """Handle zero closing price gracefully."""
        clv = calculate_clv(Decimal("2.00"), Decimal("0"))
        assert clv == Decimal("0")
