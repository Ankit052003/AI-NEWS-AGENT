# Phase 4: Article Extraction

Phase 4 adds the content-reading step after web search. The backend can now take
source URLs, fetch article pages, remove common page chrome, and return clean
article text for downstream summarization.

## What Was Added

- `ExtractedArticle` schema in `backend/app/schemas/article.py`.
- `ContentExtractionService` in `backend/app/services/content_extraction.py`.
- HTML fetching with `httpx`, redirects, timeout settings, and a project user
  agent.
- Main-text extraction from article-like tags while skipping scripts, styles,
  navigation, headers, footers, forms, iframes, and hidden content.
- Metadata capture for title, author, source, published date, extracted text,
  word count, and extraction timestamp.
- Duplicate paragraph removal and simple boilerplate filtering.
- Per-source failure handling so blocked, non-HTML, paywalled, or low-content
  pages are skipped without failing the whole research request.
- `/research` now includes an `articles` list alongside the existing `sources`
  list.

## Environment Variables

```text
CONTENT_EXTRACTION_TIMEOUT_SECONDS=10
CONTENT_EXTRACTION_MIN_WORDS=80
CONTENT_EXTRACTION_USER_AGENT=NewsResearchAgent/0.1
```

## Response Shape

`POST /research` still returns the Phase 2/3 fields, with one additive field:

```json
{
  "query": "Latest AI startup funding news this week",
  "summary": "Found 5 relevant sources. Extracted clean article text from 3 sources.",
  "report": "# Research Report...",
  "sources": [],
  "articles": [
    {
      "title": "Article title",
      "url": "https://example-news-site.com/article",
      "source": "Example News",
      "author": "Reporter Name",
      "published_date": "2026-05-11",
      "extracted_text": "Clean article body text...",
      "word_count": 842,
      "extracted_at": "2026-05-13T..."
    }
  ],
  "generated_at": "2026-05-13T..."
}
```

With `SEARCH_API_KEY` configured, the backend searches NewsAPI and then attempts
extraction for each returned source URL. Without `SEARCH_API_KEY`, the endpoint
keeps using mocked development sources and skips extraction.

## How To Verify

Run backend lint:

```powershell
cd backend
ruff check app
```

Run a local parser smoke test without making network calls:

```powershell
cd backend
python -c "from app.config import Settings; from app.schemas.research import ResearchSource; from app.services.content_extraction import ContentExtractionService; html='<html><head><title>Demo</title><meta name=\"author\" content=\"A Reporter\"></head><body><article><h1>Demo Article</h1><p>This is a useful paragraph with enough meaningful text to pass the extraction threshold for the smoke test.</p><p>This is another useful paragraph that represents the readable article body after navigation and scripts are removed.</p></article></body></html>'; svc=ContentExtractionService(Settings(content_extraction_min_words=20)); source=ResearchSource(title='Fallback title', url='https://example.com/demo', source='Example News', snippet='Demo'); article=svc.extract_from_html(source, html); print(article.title); print(article.word_count); print(article.author)"
```

Run the existing no-server API smoke test:

```powershell
cd backend
python -c "from fastapi.testclient import TestClient; from app.main import app; client=TestClient(app); r=client.post('/research', json={'query':'Latest AI startup funding news this week','max_sources':3}); print(r.status_code); print(r.json().keys())"
```

## Done Criteria

- The backend can fetch article HTML from source URLs.
- Clean readable text is extracted into a structured schema.
- Metadata is captured where available.
- Failed extraction attempts are skipped and logged.
- `/research` returns extracted article objects when live source URLs are
  available.
- The project is ready for Phase 5 article summarization and Markdown report
  generation.
