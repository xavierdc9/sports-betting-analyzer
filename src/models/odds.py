"""OddsRecord model - a snapshot of odds from a bookmaker for an event outcome."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.bookmaker import Bookmaker
    from src.models.event import Event


class OddsRecord(Base):
    __tablename__ = "odds_records"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    event_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("events.id"), nullable=False
    )
    bookmaker_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("bookmakers.id"), nullable=False
    )
    market_type: Mapped[str] = mapped_column(
        String(30), nullable=False
    )
    outcome_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )
    price: Mapped[Decimal] = mapped_column(
        Numeric(10, 4), nullable=False
    )
    point: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    event: Mapped["Event"] = relationship(back_populates="odds_records")
    bookmaker: Mapped["Bookmaker"] = relationship(
        back_populates="odds_records"
    )

    __table_args__ = (
        Index(
            "ix_odds_event_book_market_scraped",
            "event_id",
            "bookmaker_id",
            "market_type",
            "scraped_at",
        ),
    )

    def __repr__(self) -> str:
        return (
            f"<OddsRecord(outcome='{self.outcome_name}', "
            f"price={self.price}, market='{self.market_type}')>"
        )
