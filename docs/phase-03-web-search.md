# Phase 3: Web Search System

Phase 3 replaces the source collection layer with a real web search service while
keeping the existing `POST /research` API response shape stable.

## What Was Added

- `SearchResult` schema in `backend/app/schemas/search.py`.
- `WebSearchService` in `backend/app/services/web_search.py`.
- NewsAPI integration as the first search provider.
- Search result normalization into `title`, `url`, `source`, `snippet`, and
  `published_date`.
- Duplicate URL removal that ignores tracking query parameters.
- Basic relevance ranking using query-term matches and source freshness.
- Research service integration so `/research` uses live search results when
  `SEARCH_API_KEY` is configured.
- Development fallback to mocked sources when `SEARCH_API_KEY` is missing.

## Provider Configuration

The first provider is NewsAPI.

Add these values to `.env`:

```text
SEARCH_API_KEY=your-newsapi-key
SEARCH_PROVIDER=newsapi
SEARCH_API_BASE_URL=https://newsapi.org/v2/everything
SEARCH_LANGUAGE=en
SEARCH_SORT_BY=relevancy
SEARCH_TIMEOUT_SECONDS=10
```

If `SEARCH_API_KEY` is empty, the backend still runs and returns mocked sources.
That keeps local setup easy, but real Phase 3 source links require the key.

## Request Shape

The request shape is unchanged from Phase 2:

```json
{
  "query": "Latest AI startup funding news this week",
  "max_sources": 5,
  "date_range": {
    "start_date": "2026-05-01",
    "end_date": "2026-05-12"
  }
}
```

## Response Shape

The response shape is also unchanged:

```json
{
  "query": "Latest AI startup funding news this week",
  "summary": "Found 5 relevant sources...",
  "report": "# Research Report...",
  "sources": [
    {
      "title": "Article title",
      "url": "https://example-news-site.com/article",
      "source": "Example News",
      "snippet": "Article description...",
      "published_date": "2026-05-11"
    }
  ],
  "generated_at": "2026-05-12T..."
}
```

## How To Verify

Start the backend:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

In a second PowerShell window, send a request:

```powershell
$body = @{
  query = "Latest AI startup funding news this week"
  max_sources = 5
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri http://localhost:8000/research `
  -Method Post `
  -ContentType "application/json" `
  -Body $body
```

Verify these things:

- Status is successful.
- Response has `query`, `summary`, `report`, `sources`, and `generated_at`.
- `sources` has up to `max_sources` items.
- Each source has `title`, `url`, `source`, `snippet`, and `published_date`.
- With `SEARCH_API_KEY` configured, source URLs should be real news/article URLs.
- Without `SEARCH_API_KEY`, source URLs will be mocked `example.com` URLs.

Run backend lint:

```powershell
cd backend
ruff check app
```

Run a quick no-server smoke test:

```powershell
cd backend
python -c "from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); r=client.post('/research', json={'query':'Latest AI startup funding news this week','max_sources':3}); print(r.status_code); print(len(r.json()['sources'])); print(r.json().keys())"
```

Expected:

- `ruff check app` prints `All checks passed!`.
- Smoke test prints status `200`.
- Smoke test prints `3` sources.
- Smoke test response keys include `query`, `summary`, `report`, `sources`, and
  `generated_at`.

## Done Criteria

- `POST /research` can collect source links through `WebSearchService`.
- Search results are normalized into the project source format.
- Duplicate URLs are removed.
- Results are ranked before being returned.
- The backend remains usable in development without a search API key.
- The project is ready for Phase 4 article extraction.
