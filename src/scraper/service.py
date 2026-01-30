"""Scraper service that fetches odds and persists them to the database."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bookmaker import Bookmaker
from src.models.event import Event
from src.models.odds import OddsRecord
from src.models.sport import Sport
from src.scraper.odds_api import OddsApiClient
from src.scraper.schemas import EventOddsResponse, SportResponse

logger = logging.getLogger(__name__)


class ScraperService:
    """Orchestrates scraping odds data and storing it in the database."""

    def __init__(self, client: Optional[OddsApiClient] = None):
        self.client = client or OddsApiClient()

    async def sync_sports(self, session: AsyncSession) -> List[Sport]:
        """Fetch sports from the API and upsert into the database."""
        api_sports = await self.client.get_sports(include_inactive=True)
        db_sports = []

        for api_sport in api_sports:
            sport = await self._upsert_sport(session, api_sport)
            db_sports.append(sport)

        await session.flush()
        logger.info("Synced %d sports", len(db_sports))
        return db_sports

    async def scrape_odds(
        self,
        session: AsyncSession,
        sport_key: str,
        regions: str = "us",
        markets: str = "h2h,spreads,totals",
    ) -> int:
        """Scrape odds for a sport and persist all records. Returns count of new odds rows."""
        events_data = await self.client.get_odds(
            sport_key=sport_key,
            regions=regions,
            markets=markets,
        )

        if not events_data:
            logger.info("No events returned for %s", sport_key)
            return 0

        scraped_at = datetime.now(timezone.utc)
        total_records = 0

        for event_data in events_data:
            count = await self._process_event(session, event_data, scraped_at)
            total_records += count

        await session.flush()
        logger.info(
            "Scraped %d odds records across %d events for %s",
            total_records,
            len(events_data),
            sport_key,
        )
        return total_records

    async def _upsert_sport(
        self, session: AsyncSession, api_sport: SportResponse
    ) -> Sport:
        """Find or create a Sport record."""
        result = await session.execute(
            select(Sport).where(Sport.key == api_sport.key)
        )
        sport = result.scalar_one_or_none()

        if sport is None:
            sport = Sport(
                key=api_sport.key,
                title=api_sport.title,
                active=api_sport.active,
            )
            session.add(sport)
            await session.flush()
            logger.debug("Created sport: %s", api_sport.key)
        else:
            sport.active = api_sport.active

        return sport

    async def _get_or_create_bookmaker(
        self, session: AsyncSession, key: str, name: str
    ) -> Bookmaker:
        """Find or create a Bookmaker record."""
        result = await session.execute(
            select(Bookmaker).where(Bookmaker.key == key)
        )
        bookmaker = result.scalar_one_or_none()

        if bookmaker is None:
            is_exchange = "betfair_ex" in key or key in (
                "matchbook",
                "smarkets",
            )
            bookmaker = Bookmaker(
                key=key,
                name=name,
                is_exchange=is_exchange,
            )
            session.add(bookmaker)
            await session.flush()
            logger.debug("Created bookmaker: %s", key)

        return bookmaker

    async def _get_or_create_event(
        self, session: AsyncSession, event_data: EventOddsResponse, sport: Sport
    ) -> Event:
        """Find or create an Event record."""
        result = await session.execute(
            select(Event).where(Event.external_id == event_data.id)
        )
        event = result.scalar_one_or_none()

        if event is None:
            event = Event(
                external_id=event_data.id,
                sport_id=sport.id,
                home_team=event_data.home_team,
                away_team=event_data.away_team,
                commence_time=event_data.commence_time,
            )
            session.add(event)
            await session.flush()
        else:
            event.home_team = event_data.home_team
            event.away_team = event_data.away_team
            event.commence_time = event_data.commence_time

        return event

    async def _process_event(
        self,
        session: AsyncSession,
        event_data: EventOddsResponse,
        scraped_at: datetime,
    ) -> int:
        """Process a single event: upsert event/sport/bookmaker, append odds records."""
        # Ensure sport exists
        sport = await self._upsert_sport(
            session,
            SportResponse(
                key=event_data.sport_key,
                group="",
                title=event_data.sport_title,
                description="",
                active=True,
                has_outrights=False,
            ),
        )

        # Ensure event exists
        event = await self._get_or_create_event(session, event_data, sport)

        records_count = 0
        for bm_data in event_data.bookmakers:
            bookmaker = await self._get_or_create_bookmaker(
                session, bm_data.key, bm_data.title
            )

            for market in bm_data.markets:
                for outcome in market.outcomes:
                    odds_record = OddsRecord(
                        event_id=event.id,
                        bookmaker_id=bookmaker.id,
                        market_type=market.key,
                        outcome_name=outcome.name,
                        price=outcome.price,
                        point=outcome.point,
                        scraped_at=scraped_at,
                    )
                    session.add(odds_record)
                    records_count += 1

        return records_count
