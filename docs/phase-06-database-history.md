# Phase 6: Database And Research History

Phase 6 persists research queries, sources, extracted article text, summaries,
and reports so completed work can be reopened later.

## What Was Added

- SQLAlchemy database setup in `backend/app/database.py`.
- Persistent default SQLite database for local development.
- PostgreSQL support through `DATABASE_URL`.
- Alembic scaffold in `backend/alembic/`.
- SQLAlchemy models for:
  - `users`
  - `research_queries`
  - `articles`
  - `reports`
  - `user_memory`
- `ResearchHistoryService` in `backend/app/services/history.py`.
- Automatic persistence after successful `POST /research`.
- `GET /research/history` for saved report lists.
- `GET /research/reports/{report_id}` for saved report detail.

## Database Configuration

Default local development:

```text
DATABASE_URL=sqlite:///./news_agent.db
```

PostgreSQL example:

```text
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/news_research
```

The app creates tables at startup and also lazily before opening a database
session, which keeps quick `TestClient` smoke tests simple.

## API Endpoints

```text
GET /research/history?limit=20
GET /research/reports/{report_id}
```

Saved report detail includes:

- report metadata
- original query
- Markdown report content
- source list
- persisted article records
- extracted text and summary where available

## How To Verify

```powershell
cd backend
python -c "from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); r=client.post('/research', json={'query':'Latest AI startup funding news this week','max_sources':3}); data=r.json(); print(r.status_code, data['report_id']); print(client.get('/research/history').status_code); print(client.get('/research/reports/'+data['report_id']).status_code)"
```

Expected:

- `POST /research` returns `200`.
- The response includes `query_id` and `report_id`.
- History and report detail endpoints return `200`.

## Done Criteria

- Research reports remain available after backend restart.
- Sources and article summaries are saved with the report.
- The frontend has stable endpoints for history and detail pages.
