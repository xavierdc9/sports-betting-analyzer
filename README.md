# Sports Betting Analyzer

A sports betting analysis platform that scrapes odds from multiple sources, detects favorable betting opportunities (arbitrage, value bets, line movements), integrates Polymarket prediction markets, and presents everything via a React/Next.js dashboard.

## Tech Stack

- **Backend:** Python FastAPI with async SQLAlchemy
- **Database:** PostgreSQL (Neon) with Alembic migrations
- **Frontend:** React / Next.js 14 with Tailwind CSS
- **External APIs:** The Odds API, Polymarket (mock)

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- PostgreSQL database (or use SQLite for local development)

### Backend Setup

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

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend proxies API requests to `http://localhost:8000`.

### Running Tests

```bash
DATABASE_URL="sqlite+aiosqlite://" pytest tests/ -v
```

## Project Structure

```
src/
  main.py              # FastAPI app with routers and scheduler
  config.py            # Pydantic settings (env vars)
  database.py          # Async SQLAlchemy engine and session
  scheduler.py         # APScheduler for periodic scraping
  models/              # SQLAlchemy ORM models
    sport.py           # Sport categories (NFL, NBA, etc.)
    event.py           # Sporting events / games
    bookmaker.py       # Sportsbooks and exchanges
    odds.py            # Odds snapshots (append-only for line history)
    alert.py           # Detected opportunities (arb, value, movement)
  api/routes/          # FastAPI route handlers
    sports.py          # GET /api/sports
    events.py          # GET /api/events, GET /api/events/{id}
    odds.py            # GET /api/odds, GET /api/odds/event/{id}/history
    alerts.py          # GET /api/alerts, PATCH /api/alerts/{id}/read
    scraper.py         # POST /api/scraper/scrape, POST /api/scraper/analyze
    polymarket.py      # GET /api/polymarket/markets
  scraper/             # Odds scraping services
    odds_api.py        # The Odds API v4 async client
    service.py         # Scraper service with DB persistence
    schemas.py         # Pydantic models for API responses
  analysis/            # Betting analysis engine
    arbitrage.py       # Cross-bookmaker arbitrage detection
    value.py           # Value bet detection vs sharp lines
    line_movement.py   # Line movement tracking and CLV
    alert_generator.py # DB alert creation from analysis results
  polymarket/          # Prediction market integration
    mock_client.py     # Mock Polymarket data
    schemas.py         # Polymarket response schemas
frontend/              # Next.js 14 dashboard
  src/app/             # App router pages
  src/components/      # React components
  src/lib/             # API client and types
alembic/               # Database migration scripts
tests/                 # Test suite (45 tests)
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/api/sports` | List sports |
| GET | `/api/events` | List events (filter by sport, completed) |
| GET | `/api/events/{id}` | Get single event |
| GET | `/api/odds` | List odds records (filter by event, bookmaker, market) |
| GET | `/api/odds/event/{id}/history` | Odds history for line charts |
| GET | `/api/alerts` | List alerts (filter by type, unread) |
| PATCH | `/api/alerts/{id}/read` | Mark alert as read |
| POST | `/api/alerts/mark-all-read` | Mark all alerts read |
| POST | `/api/scraper/scrape` | Manually trigger odds scraping |
| POST | `/api/scraper/analyze` | Manually trigger analysis |
| GET | `/api/polymarket/markets` | List prediction markets |
| GET | `/api/polymarket/markets/{id}` | Get single prediction market |

## Environment Variables

See `.env.example` for the full list of required environment variables.
