# AI News Research Agent

An autonomous news research assistant that turns a user query into a structured,
source-backed research report.

This project is being built as a production-style AI application, not a simple
chatbot wrapper. The backend already supports a research API, live news search
through NewsAPI, source normalization, duplicate removal, relevance ranking, and
article content extraction. Future phases add AI summarization, persistence,
LangGraph orchestration, and multi-agent workflows.

## Project Snapshot

| Area | Status |
| --- | --- |
| Backend API | Implemented with FastAPI |
| Frontend | Basic Next.js research workspace |
| Web search | Implemented with NewsAPI |
| Article extraction | Implemented with clean text extraction |
| AI summarization | Planned |
| Database history | Planned |
| LangGraph workflow | Planned |
| Multi-agent system | Planned |

## Why This Project Stands Out

Most beginner AI projects stop at a chat interface. This project demonstrates a
real research pipeline with clear engineering boundaries:

- API-first backend design with typed request and response schemas
- Live web integration through a configurable search provider
- Source normalization, duplicate removal, and basic ranking
- Article fetching and clean text extraction with failure handling
- Modular service architecture ready for summarization, memory, and agents
- Documentation organized by implementation phase
- Frontend foundation for a full research product experience

## Current Features

- `GET /health` backend health check
- `POST /research` endpoint for research requests
- Pydantic schemas for request validation and structured responses
- NewsAPI-backed web search when `SEARCH_API_KEY` is configured
- Mocked source fallback when no search API key is available
- Search result normalization into title, URL, source, snippet, and date
- Duplicate URL removal that ignores common tracking parameters
- Basic relevance ranking using query terms and article freshness
- Article extraction service that removes common page chrome
- Extracted article metadata including title, author, published date, text, word
  count, and extraction timestamp
- Backend logging, validation handling, and Ruff configuration
- Basic Next.js page for the research workspace

## Example Use Case

```text
Give me the latest AI startup funding news this week.
```

Expected product flow:

```text
User query
  -> FastAPI research endpoint
  -> NewsAPI web search
  -> Source normalization and ranking
  -> Article HTML fetching
  -> Clean text extraction
  -> AI summarization and report generation
  -> Saved report history
```

The first four pipeline stages are implemented. Summarization, saved reports,
and advanced agent orchestration are planned next.

## Architecture

```text
frontend/
  Next.js research workspace
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
        |      - result normalization
        |      - deduplication
        |      - relevance ranking
        |
        +--> ContentExtractionService
               - article fetching
               - HTML cleanup
               - readable text extraction
               - metadata capture
```

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js, React, Tailwind CSS |
| Backend | FastAPI, Python |
| Validation | Pydantic |
| Search Provider | NewsAPI |
| HTTP Client | httpx |
| Linting | Ruff, ESLint |
| AI Workflow | LangGraph planned |
| LLM Providers | OpenAI or Gemini planned |
| Database | PostgreSQL planned |
| Vector Store | Chroma planned |
| Background Jobs | Redis with Celery or RQ planned |

## API Overview

### Health Check

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

### Research Request

```text
POST /research
```

Request body:

```json
{
  "query": "Latest AI startup funding news this week",
  "max_sources": 3,
  "date_range": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-13"
  }
}
```

Response shape:

```json
{
  "query": "Latest AI startup funding news this week",
  "summary": "Found 3 relevant sources...",
  "report": "# Research Report...",
  "sources": [
    {
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "Example News",
      "snippet": "Article snippet...",
      "published_date": "2026-05-12"
    }
  ],
  "articles": [
    {
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "Example News",
      "author": "Reporter Name",
      "published_date": "2026-05-12",
      "extracted_text": "Clean article body text...",
      "word_count": 850,
      "extracted_at": "2026-05-13T..."
    }
  ],
  "generated_at": "2026-05-13T..."
}
```

## Project Structure

```text
backend/
  app/
    agents/
    memory/
    models/
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
      research_service.py
      web_search.py
    utils/
    workflows/
    config.py
    main.py
  requirements.txt
  pyproject.toml

frontend/
  app/
    globals.css
    layout.tsx
    page.tsx
  package.json

docs/
  phase-01-setup.md
  phase-02-api-foundation.md
  phase-03-web-search.md
  phase-04-article-extraction.md

docker/
plan.md
README.md
```

## Run Locally

### Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Health check:

```text
http://localhost:8000/health
```

### Research API Smoke Test

```powershell
$body = @{
  query = "Latest AI startup funding news this week"
  max_sources = 3
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/research `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Without `SEARCH_API_KEY`, the API returns mocked `example.com` sources so local
development still works. With `SEARCH_API_KEY`, it returns live NewsAPI source
links and attempts to extract clean article text from those URLs.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:3000
```

## Environment Variables

Create a `.env` file from `.env.example` and fill in the values needed for each
feature.

```text
APP_NAME="News Research Agent"
ENVIRONMENT=development
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO

OPENAI_API_KEY=
GEMINI_API_KEY=
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

DATABASE_URL=
REDIS_URL=
```

## Verification

Backend lint:

```powershell
cd backend
ruff check app
```

Backend no-server smoke test:

```powershell
cd backend
python -c "from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); r=client.post('/research', json={'query':'Latest AI startup funding news this week','max_sources':3}); print(r.status_code); print(r.json().keys())"
```

Frontend checks:

```powershell
cd frontend
npm run lint
npm run build
```

## Implementation Roadmap

Completed:

- Phase 1: Project setup and repository structure
- Phase 2: Backend API foundation
- Phase 3: Web search system
- Phase 4: Article extraction

Next:

- Phase 5: AI summarization and Markdown report MVP
- Phase 6: PostgreSQL database and research history
- Phase 7: Full frontend research experience
- Phase 8: LangGraph workflow orchestration
- Phase 9: Multi-agent architecture

## Engineering Highlights

- The API response shape is designed to survive future phases without large
  frontend rewrites.
- Services are isolated by responsibility, which makes the project ready for
  testing, workflow orchestration, and agent decomposition.
- External integrations fail gracefully. Missing search credentials use mocked
  sources, and failed article extractions are skipped rather than breaking the
  entire research request.
- The project follows an incremental build plan: reliable pipeline first,
  advanced AI architecture later.

## Author

Ankit Kumar
