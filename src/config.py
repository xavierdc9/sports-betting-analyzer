"""Application configuration loaded from environment variables."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables or .env file."""

    # Database
    database_url: str = "postgresql+asyncpg://localhost/sports_betting"

    # The Odds API
    the_odds_api_key: str = ""

    # Betfair Exchange
    betfair_api_key: str = ""
    betfair_session_token: str = ""

    # Pinnacle
    pinnacle_api_key: str = ""

    # App
    app_version: str = "0.1.0"
    debug: bool = False

    # CORS
    cors_origins: List[str] = [
        "https://follow-the-flows.vercel.app",
        "http://localhost:3000",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


settings = Settings()
