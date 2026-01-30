"""APScheduler integration for periodic odds scraping and analysis."""

from __future__ import annotations

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.analysis.alert_generator import generate_arb_alerts, generate_value_alerts
from src.database import async_session_factory
from src.scraper.service import ScraperService

logger = logging.getLogger(__name__)

# Default sports to scrape
DEFAULT_SPORTS = [
    "americanfootball_nfl",
    "basketball_nba",
    "baseball_mlb",
    "icehockey_nhl",
]

scheduler = AsyncIOScheduler()


async def scrape_and_analyze_job() -> None:
    """Scheduled job: scrape odds for all configured sports and run analysis."""
    service = ScraperService()

    async with async_session_factory() as session:
        try:
            # Sync sports catalog
            await service.sync_sports(session)
            await session.commit()
        except Exception:
            logger.exception("Failed to sync sports")
            await session.rollback()

        # Scrape odds for each sport
        for sport_key in DEFAULT_SPORTS:
            try:
                count = await service.scrape_odds(session, sport_key=sport_key)
                await session.commit()
                logger.info("Scraped %d odds for %s", count, sport_key)
            except Exception:
                logger.exception("Failed to scrape %s", sport_key)
                await session.rollback()

        # Run analysis and generate alerts
        try:
            arb_alerts = await generate_arb_alerts(session)
            value_alerts = await generate_value_alerts(session)
            await session.commit()
            logger.info(
                "Analysis complete: %d arb alerts, %d value alerts",
                len(arb_alerts),
                len(value_alerts),
            )
        except Exception:
            logger.exception("Failed to run analysis")
            await session.rollback()


def start_scheduler(interval_minutes: int = 5) -> None:
    """Start the scheduler with periodic scraping job."""
    scheduler.add_job(
        scrape_and_analyze_job,
        "interval",
        minutes=interval_minutes,
        id="scrape_and_analyze",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Scheduler started (interval: %d min)", interval_minutes)


def stop_scheduler() -> None:
    """Stop the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped")
