# Phase 5: Summarization And Report MVP

Phase 5 turns extracted source text into a usable cited research report.

## What Was Added

- `ArticleSummary` response schema with citation index, summary, key points, and
  source metadata.
- `SummarizationService` in `backend/app/services/summarization.py`.
- OpenAI-compatible JSON summarization when `DEFAULT_LLM_PROVIDER=openai`,
  `OPENAI_API_KEY`, and a non-mock `DEFAULT_MODEL` are configured.
- Deterministic local summarization fallback for development and offline use.
- Markdown report generation with these sections:
  - Executive Summary
  - Key Findings
  - Important Articles
  - Emerging Trends
  - Source List
- Source citations formatted as `[1]`, `[2]`, and so on.
- Basic cross-source trend detection from repeated article themes.

## Environment Variables

```text
OPENAI_API_KEY=
OPENAI_API_BASE_URL=https://api.openai.com/v1/chat/completions
DEFAULT_LLM_PROVIDER=mock
DEFAULT_MODEL=mock-news-researcher
LLM_TIMEOUT_SECONDS=30
LLM_TEMPERATURE=0.2
```

The default `mock` provider uses the local summarizer. To use OpenAI, set
`DEFAULT_LLM_PROVIDER=openai`, choose an OpenAI chat model in `DEFAULT_MODEL`,
and provide `OPENAI_API_KEY`.

## Response Additions

`POST /research` now includes `article_summaries`:

```json
{
  "article_summaries": [
    {
      "citation_index": 1,
      "title": "Article title",
      "url": "https://example.com/article",
      "source": "Example News",
      "summary": "Short source-backed summary...",
      "key_points": ["Important fact from the article..."],
      "published_date": "2026-05-15"
    }
  ]
}
```

## How To Verify

```powershell
cd backend
ruff check app
python -c "from app.schemas.research import ResearchRequest; from app.services.research_service import ResearchService; r=ResearchService().generate_mock_report(ResearchRequest(query='Latest AI startup funding news this week', max_sources=3)); print(len(r.article_summaries)); print(r.report.splitlines()[0])"
```

Expected:

- Ruff passes.
- The mock report returns article summaries.
- The report starts with `# Research Report`.

## Done Criteria

- Articles and snippets are summarized into structured objects.
- The final report is readable Markdown.
- The report includes citations and a source list.
- The backend works without an LLM key and can use OpenAI when configured.
