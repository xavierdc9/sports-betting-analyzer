# Sports Betting Analyzer

A sports betting analysis platform that scrapes odds from multiple sources, detects favorable betting opportunities (arbitrage, value bets, line movements), and presents everything via a dashboard.

## Tech Stack

- **Backend:** Python FastAPI with async SQLAlchemy
- **Database:** PostgreSQL (Neon) with Alembic migrations
- **Frontend:** React / Next.js (planned)

## Quick Start

### Prerequisites
- Python 3.8+
- PostgreSQL database (or use SQLite for local development)

### Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env with your database URL and API keys

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn src.main:app --reload
```

### Running Tests

```bash
DATABASE_URL="sqlite+aiosqlite://" pytest tests/ -v
```

## Project Structure

```
src/
  main.py          # FastAPI application entry point
  config.py        # Pydantic settings (env vars)
  database.py      # Async SQLAlchemy engine and session
  models/          # SQLAlchemy ORM models
    sport.py       # Sport categories (NFL, NBA, etc.)
    event.py       # Sporting events / games
    bookmaker.py   # Sportsbooks and exchanges
    odds.py        # Odds snapshots (append-only for line history)
    alert.py       # Detected opportunities (arb, value, movement)
  api/             # FastAPI route handlers (planned)
  scraper/         # Odds scraping services (planned)
  analysis/        # Arbitrage & value bet detection (planned)
  polymarket/      # Prediction market integration (planned)
alembic/           # Database migration scripts
tests/             # Test suite
```

## API Endpoints

- `GET /health` - Health check (`{"status": "ok", "version": "0.1.0"}`)

## Environment Variables

See `.env.example` for the full list of required environment variables.
