"""FastAPI application entry point for the Sports Betting Analyzer API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.api.routes import alerts, events, odds, scraper, sports
from src.config import settings
from src.database import engine
from src.scheduler import start_scheduler, stop_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Verify database connectivity on startup and cleanup on shutdown."""
    # Startup
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connection verified")
    except Exception as e:
        logger.warning("Database connection failed: %s", e)

    # Start scheduled scraping if API key is configured
    if settings.the_odds_api_key:
        start_scheduler()

    yield

    # Shutdown
    stop_scheduler()
    await engine.dispose()


app = FastAPI(
    title="Sports Betting Analyzer API",
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register API routers
app.include_router(sports.router)
app.include_router(events.router)
app.include_router(odds.router)
app.include_router(alerts.router)
app.include_router(scraper.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.app_version}
