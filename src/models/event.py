"""Event model - represents a sporting event (game/match)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.alert import Alert
    from src.models.odds import OddsRecord
    from src.models.sport import Sport


class Event(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    external_id: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False
    )
    sport_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("sports.id"), nullable=False
    )
    home_team: Mapped[str] = mapped_column(String(150), nullable=False)
    away_team: Mapped[str] = mapped_column(String(150), nullable=False)
    commence_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    sport: Mapped["Sport"] = relationship(back_populates="events")
    odds_records: Mapped[List["OddsRecord"]] = relationship(
        back_populates="event"
    )
    alerts: Mapped[List["Alert"]] = relationship(back_populates="event")

    def __repr__(self) -> str:
        return f"<Event('{self.away_team}' @ '{self.home_team}')>"
