# AI News Research Agent

An autonomous AI news research product that turns a user query into a saved,
source-backed Markdown research report.

The MVP is complete through Phase 7 of the project plan. It can accept a
research query, collect sources, extract article text, summarize findings,
generate a cited report, persist the result, and let the user reopen saved
reports from a Next.js interface.

## MVP Status

| Phase | Status | Result |
| --- | --- | --- |
| Phase 1 | Complete | FastAPI backend and Next.js frontend structure |
| Phase 2 | Complete | Typed `POST /research` API contract |
| Phase 3 | Complete | NewsAPI search, source normalization, deduping, ranking |
| Phase 4 | Complete | Article fetching and clean text extraction |
| Phase 5 | Complete | Article summaries and cited Markdown reports |
| Phase 6 | Complete | SQLAlchemy persistence and research history APIs |
| Phase 7 | Complete | Browser UI for research, saved reports, detail view, dashboard |

Advanced phases such as LangGraph orchestration, multi-agent workflows, memory,
RAG, background jobs, scheduling, and exports are intentionally left for the next
stage after the MVP pipeline works end to end.

## What It Does

Example query:

```text
Give me the latest AI startup funding news this week.
```

MVP flow:

```text
User query
  -> FastAPI research endpoint
  -> Web search through NewsAPI when configured
  -> Mock source fallback when no search key is available
  -> Source normalization, deduplication, and ranking
  -> Article HTML fetching and text extraction
  -> Article-level summarization
  -> Markdown report generation with citations
  -> Database persistence
  -> Frontend report browsing and dashboard
```

## Why This Project Is Recruiter-Friendly

This is not just a chatbot wrapper. It demonstrates product-minded AI
engineering across the full stack:

- API-first backend design with typed Pydantic request and response schemas.
- Real web integration with a configurable search provider.
- Robust fallback behavior so the app works without paid API keys.
- Article extraction with timeout handling, content filtering, and skipped
  failures instead of broken research runs.
- Report generation that keeps citations tied to source links.
- Persistence of research queries, sources, extracted article text, summaries,
  and final reports.
- A usable frontend with query submission, loading states, saved report list,
  report detail page, source browsing, and a lightweight dashboard.
- Modular services that are ready to evolve into LangGraph nodes and specialized
  agents in later phases.

## Current Features

Backend:

- `GET /health` health check.
- `POST /research` to run a research request.
- `GET /research/history` to list saved reports.
- `GET /research/reports/{report_id}` to reopen one saved report.
- NewsAPI-backed web search when `SEARCH_API_KEY` is configured.
- Mocked development sources when no search key is present.
- Article extraction with `httpx` and a lightweight HTML parser.
- Local deterministic summarization fallback.
- Optional OpenAI-compatible summarization path.
- SQLAlchemy models for users, research queries, articles, reports, and user
  memory.
- Alembic scaffold for database migrations.

Frontend:

- Main research workspace at `/`.
- Saved reports page at `/reports`.
- Saved report detail page at `/reports/[id]`.
- Activity dashboard at `/dashboard`.
- Markdown report rendering.
- Source link panels and extracted-article metadata.

## Architecture

```text
frontend/
  Next.js App Router
  Tailwind CSS
  API client
  Report pages and dashboard
        |
        v
backend/
  FastAPI routes
        |
        v
  ResearchService
        |
        +--> WebSearchService
        |      - NewsAPI integration
        |      - normalization
        |      - duplicate removal
        |      - relevance ranking
        |
        +--> ContentExtractionService
        |      - HTML fetching
        |      - page cleanup
        |      - article text extraction
        |      - metadata capture
        |
        +--> SummarizationService
        |      - article summaries
        |      - key points
        |      - Markdown report synthesis
        |
        +--> ResearchHistoryService
               - SQLAlchemy persistence
               - saved report list
               - saved report detail
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js, React, Tailwind CSS |
| Backend | FastAPI, Python |
| Validation | Pydantic |
| Search | NewsAPI |
| HTTP | httpx |
| Persistence | SQLAlchemy, Alembic |
| Local DB | SQLite |
| Production DB Target | PostgreSQL via `DATABASE_URL` |
| LLM | Local fallback by default, OpenAI optional |
| Linting | Ruff, ESLint |

## API Overview

### Health

```text
GET /health
```

Example response:

```json
{
  "status": "ok",
  "service": "News Research Agent",
  "environment": "development"
}
```

### Run Research

```text
POST /research
```

Request:

```json
{
  "query": "Latest AI startup funding news this week",
  "max_sources": 3,
  "date_range": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-15"
  }
}
```

Response includes:

- `query_id`
- `report_id`
- `summary`
- Markdown `report`
- normalized `sources`
- extracted `articles`
- structured `article_summaries`
- `generated_at`

### Saved Reports

```text
GET /research/history
GET /research/reports/{report_id}
```

The saved report detail includes the original query, final report, source list,
article records, summaries, extracted text where available, and timestamps.

## Project Structure

```text
backend/
  app/
    agents/
    memory/
    models/
      research.py
    rag/
    routes/
      health.py
      research.py
    schemas/
      article.py
      research.py
      search.py
    services/
      content_extraction.py
      history.py
      research_service.py
      summarization.py
      web_search.py
    utils/
    workflows/
    config.py
    database.py
    main.py
  alembic/
  alembic.ini
  requirements.txt
  pyproject.toml

frontend/
  app/
    dashboard/
    reports/
    globals.css
    layout.tsx
    page.tsx
  components/
  services/
  package.json

docs/
  phase-01-setup.md
  phase-02-api-foundation.md
  phase-03-web-search.md
  phase-04-article-extraction.md
  phase-05-summarization-report.md
  phase-06-database-history.md
  phase-07-frontend-mvp.md
```

## Run Locally

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Health check:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### 2. Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm.cmd run dev
```

Open:

```text
http://localhost:3000
```

## Environment Variables

Create `.env` from `.env.example`.

```text
APP_NAME="News Research Agent"
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
LOG_LEVEL=INFO

OPENAI_API_KEY=
GEMINI_API_KEY=
OPENAI_API_BASE_URL=https://api.openai.com/v1/chat/completions

SEARCH_API_KEY=
SEARCH_PROVIDER=newsapi
SEARCH_API_BASE_URL=https://newsapi.org/v2/everything
SEARCH_LANGUAGE=en
SEARCH_SORT_BY=relevancy
SEARCH_TIMEOUT_SECONDS=10

CONTENT_EXTRACTION_TIMEOUT_SECONDS=10
CONTENT_EXTRACTION_MIN_WORDS=80
CONTENT_EXTRACTION_USER_AGENT=NewsResearchAgent/0.1

DEFAULT_LLM_PROVIDER=mock
DEFAULT_MODEL=mock-news-researcher
DEFAULT_MAX_SOURCES=5
LLM_TIMEOUT_SECONDS=30
LLM_TEMPERATURE=0.2

DATABASE_URL=sqlite:///./news_agent.db
REDIS_URL=

NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

API keys are optional for local Phase 7 verification. Without `SEARCH_API_KEY`,
the backend uses mocked sources and still generates and saves reports. For live
news, set `SEARCH_API_KEY`. For OpenAI summaries, set
`DEFAULT_LLM_PROVIDER=openai`, provide `OPENAI_API_KEY`, and choose an OpenAI
chat model in `DEFAULT_MODEL`.

## Verification

Backend:

```powershell
cd backend
ruff check app alembic
python -m compileall app alembic
```

Backend smoke test:

```powershell
cd backend
python -c "from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); r=client.post('/research', json={'query':'Latest AI startup funding news this week','max_sources':3}); data=r.json(); print(r.status_code, data['report_id']); print(client.get('/research/history').status_code); print(client.get('/research/reports/'+data['report_id']).status_code)"
```

Frontend:

```powershell
cd frontend
npm.cmd run lint
npm.cmd run build
```

## Roadmap

Completed:

- Phase 1: Project setup and repository structure.
- Phase 2: Backend API foundation.
- Phase 3: Web search system.
- Phase 4: Article extraction.
- Phase 5: Summarization and Markdown report MVP.
- Phase 6: Database and research history.
- Phase 7: Frontend MVP.

Next:

- Phase 8: Convert the pipeline into a LangGraph workflow.
- Phase 9: Split workflow responsibilities into specialized agents.
- Phase 10: Add memory and RAG over previous research.
- Phase 11: Add deeper trend analytics and charts.
- Phase 12+: Add background jobs, scheduling, exports, credibility controls,
  testing, deployment, and portfolio polish.

## Engineering Notes

- The response shape is intentionally stable so the frontend can use the same
  report data immediately after generation and later from saved history.
- Search, extraction, summarization, and persistence live in separate services,
  making the current MVP ready for workflow orchestration.
- External failures are isolated. Missing search credentials use mocked sources,
  and extraction failures are logged and skipped per source.
- SQLite is the default for easy local demos, while the schema and SQLAlchemy
  setup are prepared for PostgreSQL.

## Author

Ankit Kumar Singh
