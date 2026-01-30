# Sports Betting Analyzer - Shared Context

## Project Overview
A sports betting analysis platform that scrapes odds from multiple sources, detects favorable betting opportunities (arbitrage, value bets, line movements), integrates Polymarket prediction markets (scaffolded/mock), and presents everything via a React/Next.js dashboard.

## Tech Stack
- **Frontend:** React / Next.js 14 with Tailwind CSS
- **Backend:** Python FastAPI
- **Database:** Neon Postgres (connection via `DATABASE_URL` env var)
- **ORM:** SQLAlchemy (async) + Alembic migrations
- **External APIs:** The Odds API, Betfair Exchange API, Pinnacle API (all via env-configured keys)
- **Testing:** pytest (backend), 45 tests passing

## Architecture Decisions
- **Monorepo layout:** `src/` for Python backend, `frontend/` for Next.js app
- **FastAPI** chosen over Node.js for backend - better async support, strong typing with Pydantic, native Python data science ecosystem
- **SQLAlchemy** async models with Alembic migrations for schema management
- **APScheduler** for scheduled scraping jobs within the FastAPI process (5-min interval)
- **UUID primary keys** for all tables (distributed-friendly)
- **Decimal odds storage** using DECIMAL(10,4) to avoid floating point issues
- **Append-only OddsRecord** table - each scrape creates new rows for full line movement history

## Database Schema (5 Tables)
1. **Sport** - Sports catalog (key, title, active)
2. **Event** - Games/matches with teams, start time, sport FK
3. **Bookmaker** - Sportsbook registry (key, name, is_exchange flag)
4. **OddsRecord** - Core data: odds snapshots per event/bookmaker/market with composite index on (event_id, bookmaker_id, market_type, scraped_at)
5. **Alert** - Generated alerts (arbitrage, value_bet, line_movement) with JSONB details

## Project Roadmap (Ordered by Priority)

### Phase 1: Foundation
- [x] Task 0: Project skeleton created
- [x] Task 1: Database schema + FastAPI project bootstrap
- [x] Task 2: Odds scraper service (The Odds API)
- [x] Task 3: Core analysis engine (arbitrage, value bets, CLV)

### Phase 2: API + Backend Services
- [x] Task 4: RESTful API endpoints (odds, events, alerts)
- [x] Task 5: Scheduled scraping + line movement tracking
- [x] Task 6: Alert/notification system (covered by alert_generator)

### Phase 3: Polymarket + Frontend
- [x] Task 7: Polymarket integration scaffolding (mock)
- [x] Task 8: Next.js frontend setup + dashboard layout
- [x] Task 9: Odds comparison table + arb calculator UI (part of Task 8)
- [x] Task 10: Alerts UI + Polymarket viewer (part of Task 8)

### Phase 4: Integration + Polish
- [ ] Task 12: End-to-end integration testing
- [x] Task 13: Vercel deployment config

## Current Status
- **Current Phase:** Phase 4 - Integration + Polish
- **Active Task:** Task 12 - E2E testing (remaining)
- **Blockers:** None
- **Tests:** 45 passing

## API Endpoints (13 total)
- GET /health
- GET /api/sports
- GET /api/events, GET /api/events/{id}
- GET /api/odds, GET /api/odds/event/{id}/history
- GET /api/alerts, PATCH /api/alerts/{id}/read, POST /api/alerts/mark-all-read
- POST /api/scraper/scrape, POST /api/scraper/analyze
- GET /api/polymarket/markets, GET /api/polymarket/markets/{id}

## Key File Locations
- Backend entry point: `src/main.py`
- DB models: `src/models/`
- DB config: `src/database.py`
- Settings: `src/config.py`
- API routes: `src/api/routes/`
- Scraper modules: `src/scraper/`
- Analysis engine: `src/analysis/`
- Polymarket mock: `src/polymarket/`
- Scheduler: `src/scheduler.py`
- Frontend app: `frontend/src/`
- Alembic config: `alembic/`
- Tests: `tests/`

## Environment Variables Required
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
THE_ODDS_API_KEY=xxx
BETFAIR_API_KEY=xxx
BETFAIR_SESSION_TOKEN=xxx
PINNACLE_API_KEY=xxx
```

## Completed Tasks Log
- **Task 0** (Iteration 0): Project skeleton
- **Task 1** (Iteration 1): DB schema + FastAPI bootstrap - `567929e`, `a4cb749`
- **Task 2** (Iteration 2): Odds scraper service - `691b877`
- **Task 3** (Iteration 3): Analysis engine - `629d552`
- **Task 4** (Iteration 4): REST API endpoints - `ee75e16`
- **Task 5** (Iteration 5): Scheduler + alerts - `c7940b3`
- **Task 7** (Iteration 6): Polymarket mock - `cd31d21`
- **Task 8** (Iteration 7): Next.js frontend - `44562ea`
- **Task 13** (Iteration 8): Vercel config + README - `5016695`, `3b5808a`
