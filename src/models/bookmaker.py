"""Bookmaker model - represents a sportsbook or exchange."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, List

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.odds import OddsRecord


class Bookmaker(Base):
    __tablename__ = "bookmakers"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    key: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_exchange: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    odds_records: Mapped[List["OddsRecord"]] = relationship(
        back_populates="bookmaker"
    )

    def __repr__(self) -> str:
        return f"<Bookmaker(key='{self.key}', name='{self.name}')>"
