# Phase 7: Frontend MVP

Phase 7 replaces the static first page with a usable research product interface.

## What Was Added

- Main research workspace at `/`.
- Query input, max-source control, example query shortcuts, loading state, and
  error state.
- API client in `frontend/services/api.ts`.
- Markdown report renderer in `frontend/components/ReportMarkdown.tsx`.
- Saved report list at `/reports`.
- Saved report detail page at `/reports/[id]`.
- Basic activity dashboard at `/dashboard`.
- Shared navigation in the root layout.
- Source link panels and extracted article summaries on detail pages.

## Frontend Routes

```text
/
  Run research and read the generated report.

/reports
  Browse saved reports.

/reports/[id]
  Reopen one saved report with source list and article records.

/dashboard
  View total reports, sources, extracted articles, and frequent query topics.
```

## Configuration

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## How To Verify

```powershell
cd frontend
npm run lint
npm run build
```

If PowerShell blocks `npm.ps1`, use:

```powershell
npm.cmd run lint
npm.cmd run build
```

## Done Criteria

- A user can run a research query from the browser.
- The generated report is displayed with citations and sources.
- Saved reports can be listed and reopened.
- The dashboard shows basic saved-report activity.
