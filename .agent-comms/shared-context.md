# Sports Betting Analyzer - Shared Context

## Project Overview
A sports betting analysis platform that scrapes odds from multiple sources, detects favorable betting opportunities (arbitrage, value bets, line movements), integrates Polymarket prediction markets (scaffolded/mock), and presents everything via a React/Next.js dashboard.

## Tech Stack
- **Frontend:** React / Next.js (deployed to Vercel)
- **Backend:** Python FastAPI
- **Database:** Neon Postgres (connection via `DATABASE_URL` env var)
- **ORM:** SQLAlchemy (async) + Alembic migrations
- **External APIs:** The Odds API, Betfair Exchange API, Pinnacle API (all via env-configured keys)
- **Testing:** pytest (backend), Jest/React Testing Library (frontend)

## Architecture Decisions
- **Monorepo layout:** `src/` for Python backend, `frontend/` for Next.js app
- **FastAPI** chosen over Node.js for backend - better async support, strong typing with Pydantic, native Python data science ecosystem
- **SQLAlchemy** async models with Alembic migrations for schema management
- **APScheduler** for scheduled scraping jobs within the FastAPI process
- **WebSockets** (FastAPI + Next.js) for real-time odds push to dashboard
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
- [ ] **Task 1: Database schema + FastAPI project bootstrap** <- ACTIVE
- [ ] Task 2: Odds scraper service (The Odds API first)
- [ ] Task 3: Core analysis engine (arbitrage, value bets, CLV)

### Phase 2: API + Backend Services
- [ ] Task 4: RESTful API endpoints (odds, events, alerts)
- [ ] Task 5: Scheduled scraping + line movement tracking
- [ ] Task 6: Alert/notification system

### Phase 3: Polymarket + Frontend
- [ ] Task 7: Polymarket integration scaffolding (mock)
- [ ] Task 8: Next.js frontend setup + dashboard layout
- [ ] Task 9: Odds comparison table + arb calculator UI
- [ ] Task 10: Historical charts + line movement visualization
- [ ] Task 11: Alerts UI + Polymarket viewer (mock data)

### Phase 4: Integration + Polish
- [ ] Task 12: End-to-end integration testing
- [ ] Task 13: Vercel deployment config + final polish

## Current Status
- **Current Phase:** Phase 1 - Foundation
- **Active Task:** Task 1 - Database schema + FastAPI project bootstrap
- **Iteration:** 1 / 50
- **Blockers:** None

## Key File Locations
- Backend entry point: `src/main.py` (to be created in Task 1)
- DB models: `src/models/` (to be created in Task 1)
- DB config: `src/database.py` (to be created in Task 1)
- Settings: `src/config.py` (to be created in Task 1)
- API routes: `src/api/routes/` (Task 4)
- Scraper modules: `src/scraper/` (Task 2)
- Analysis engine: `src/analysis/` (Task 3)
- Polymarket mock: `src/polymarket/` (Task 7)
- Frontend app: `frontend/` (Task 8)
- Alembic config: `alembic/` (to be created in Task 1)
- Tests: `tests/` (ongoing)

## Environment Variables Required
```
DATABASE_URL=postgresql+asyncpg://user:pass@host/dbname
THE_ODDS_API_KEY=xxx
BETFAIR_API_KEY=xxx
BETFAIR_SESSION_TOKEN=xxx
PINNACLE_API_KEY=xxx
```

## Completed Tasks Log
- **Task 0** (Iteration 0): Project skeleton - empty directory structure created
