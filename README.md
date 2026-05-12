# AI-NEWS-AGENT

An AI-powered research assistant that turns a news query into a source-backed market research report.

This project is designed to go beyond a simple chatbot. The goal is to build a real research pipeline that can search the web, collect reliable articles, extract clean content, summarize findings, identify trends, and save reports for future use.

## Why This Project Matters

Recruiters and engineers can use this project to quickly see my ability to build:

- AI workflow systems, not just prompt wrappers
- FastAPI backend services
- Next.js frontend applications
- Research pipelines with search, extraction, summarization, and reporting
- Scalable architecture for agents, memory, RAG, background jobs, and analytics

## Current Status

The project is currently in the foundation stage.

Completed:

- FastAPI backend setup
- Backend health check endpoint
- Mocked `POST /research` API with typed request and response schemas
- NewsAPI-backed web search service for collecting article source links
- Search result normalization, duplicate URL removal, and basic relevance ranking
- Next.js frontend setup
- Basic research workspace UI
- Environment configuration structure
- Clean project folders for future agents, workflows, RAG, memory, routes, services, and schemas
- Phase 1 setup notes in `docs/phase-01-setup.md`
- Phase 2 API foundation notes in `docs/phase-02-api-foundation.md`
- Phase 3 web search notes in `docs/phase-03-web-search.md`
- Basic ignore rules and backend Ruff configuration

In progress / planned:

- Article extraction
- AI summarization
- Markdown report generation
- Report history with PostgreSQL
- LangGraph workflow orchestration
- Multi-agent research system

## Product Vision

Example query:

```text
Give me the latest AI startup funding news this week.
```

Expected result:

- Relevant news sources
- Clean article summaries
- Key findings
- Emerging trends
- Source citations
- Saved research report

## Tech Stack

| Area | Technology |
| --- | --- |
| Frontend | Next.js, React, Tailwind CSS |
| Backend | FastAPI, Python |
| AI Workflow | LangGraph planned |
| LLM Providers | OpenAI or Gemini planned |
| Database | PostgreSQL planned |
| Vector Search | Chroma planned |
| Cache / Jobs | Redis + Celery or RQ planned |
| Deployment | Docker planned |

## Architecture

The app follows a simple flow: the user asks a research question, the backend gathers and analyzes news sources, and the frontend shows a clean report.

```text
User asks a question
        |
        v
Frontend sends the query
        |
        v
Backend runs the research pipeline
        |
        v
Search news -> Read articles -> Summarize -> Find trends
        |
        v
Generate a source-backed report
        |
        v
Save report history and show it to the user
```

### Simple Breakdown

| Part | What It Does |
| --- | --- |
| Frontend | Lets the user enter a research question and view reports |
| Backend | Receives the query and controls the research process |
| Search Service | Finds relevant news articles from the web |
| Extraction Service | Reads articles and removes unnecessary page content |
| AI Summarizer | Creates short, useful summaries from the articles |
| Report Generator | Combines findings into a final Markdown report |
| Database | Saves reports so users can open them again later |

### Planned Agent System

Later, the research pipeline will be split into focused AI agents:

| Agent | Job |
| --- | --- |
| Query Planner | Understands what the user wants |
| Web Search Agent | Finds useful sources |
| Content Agent | Extracts clean article text |
| Summary Agent | Summarizes the information |
| Trend Agent | Finds repeated patterns |
| Report Agent | Writes the final report |
| Memory Agent | Remembers past research |

## Project Structure

```text
frontend/
  app/
  components/
  hooks/
  services/
  styles/

backend/
  app/
    agents/
    workflows/
    rag/
    memory/
    routes/
    models/
    schemas/
    services/
    utils/
    config.py
    main.py
  requirements.txt

docker/
docs/
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
GET http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "News Research Agent",
  "environment": "development"
}
```

Backend lint:

```powershell
cd backend
ruff check app
```

Research request:

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

With `SEARCH_API_KEY` configured, this endpoint returns live NewsAPI source
links. Without a key, it falls back to mocked `example.com` sources so local
development still works.

### Frontend

```powershell
cd frontend
npm install
npm run dev
```

If PowerShell blocks `npm.ps1`, use `npm.cmd install` and `npm.cmd run dev`.

Open:

```text
http://localhost:3000
```

## Environment Variables

Copy `.env.example` to `.env` and fill values as features are added.

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

DEFAULT_LLM_PROVIDER=mock
DEFAULT_MODEL=mock-news-researcher
DEFAULT_MAX_SOURCES=5

DATABASE_URL=
REDIS_URL=
```

## MVP Roadmap

1. Define the research niche and report format
2. Build the FastAPI and Next.js foundation
3. Add a research request and response API
4. Integrate web search
5. Extract clean article content
6. Generate AI summaries and Markdown reports
7. Save reports and research history
8. Build a usable frontend report experience

## Future Improvements

- LangGraph-based workflow orchestration
- Multi-agent research pipeline
- RAG over previous reports
- Source credibility scoring
- Trend analytics dashboard
- Background jobs with live progress
- Scheduled research reports
- PDF export and email delivery
- Dockerized deployment
- Automated tests

## What I Want To Demonstrate

This project shows how I think about building production-style AI applications: start with a reliable end-to-end pipeline, keep the architecture modular, add agents only after the core workflow works, and make every output traceable to real sources.

## Author

Ankit Kumar
