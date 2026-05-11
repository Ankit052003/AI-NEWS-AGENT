# Phase 2: Backend API Foundation

Phase 2 adds the first real backend contract for the research product. The endpoint still returns mocked data, but the shape is designed to survive later phases when web search, article extraction, LLM summarization, and persistence become real.

## What Was Added

- `POST /research` endpoint in `backend/app/routes/research.py`.
- Research request and response schemas in `backend/app/schemas/research.py`.
- Mock research generation service in `backend/app/services/research_service.py`.
- Basic route-level error handling for research generation failures.
- Validation logging for malformed API requests.
- Application settings for future API keys, default model configuration, max sources, and log level.
- README updates with the new API example.

## Request Shape

```json
{
  "query": "Latest AI startup funding news this week",
  "user_id": "optional-user-id",
  "max_sources": 5,
  "date_range": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-12"
  }
}
```

Required field:

- `query`

Optional fields:

- `user_id`
- `max_sources`
- `date_range.start_date`
- `date_range.end_date`

Validation rules:

- `query` must be between 3 and 500 characters.
- `max_sources` must be between 1 and 20.
- `date_range.start_date` cannot be after `date_range.end_date`.

## Response Shape

```json
{
  "query": "Latest AI startup funding news this week",
  "summary": "Mock research report...",
  "report": "# Research Report...",
  "sources": [
    {
      "title": "Mock: AI infrastructure startup funding update",
      "url": "https://example.com/ai-infrastructure-funding",
      "source": "Example Tech News",
      "snippet": "Placeholder result...",
      "published_date": "2026-05-11"
    }
  ],
  "generated_at": "2026-05-12T..."
}
```

## Why The Mock Service Exists

The mock service lets the frontend and future backend pipeline build against a stable API before external dependencies are added. This is intentional:

- Phase 3 can replace mock sources with real web search results.
- Phase 4 can attach extracted article text.
- Phase 5 can replace the mock report with LLM-generated Markdown.
- Phase 6 can save the same response shape to the database.

## How To Test

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Send a research request:

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

Run backend lint:

```powershell
cd backend
ruff check app
```

## Done Criteria

- `POST /research` accepts a valid research query.
- The endpoint returns a structured response with `query`, `summary`, `report`, `sources`, and `generated_at`.
- Invalid requests return validation errors.
- Backend lint passes.
- The API is ready for Phase 3 web search integration.
