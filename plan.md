# Autonomous AI News Research Agent

## Chronological Project Plan

This project is an autonomous AI research system that can take a user query, search the web, collect relevant articles, extract clean content, summarize findings, detect trends, generate a report, and store research history.

The most important rule for building this project:

Build a reliable end-to-end research pipeline first. Then convert it into a multi-agent LangGraph system.

Do not start with the most advanced architecture. Start with a simple working product, then make it smarter phase by phase.

---

## Final Product Vision

The user should be able to ask something like:

```text
Give me the latest AI startup funding news this week.
```

The system should:

1. Understand the research goal.
2. Search the web for relevant sources.
3. Fetch article content.
4. Remove duplicates and low-quality results.
5. Summarize individual articles.
6. Combine findings into a final research report.
7. Detect trends and patterns.
8. Save the report and research history.
9. Optionally schedule recurring reports.
10. Optionally email reports to the user.

---

## Recommended Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js + Tailwind |
| Backend | FastAPI |
| AI Workflow | LangGraph |
| LLM Provider | OpenAI or Gemini |
| Database | PostgreSQL |
| Vector Database | Chroma first, Pinecone later if needed |
| Cache | Redis |
| Background Jobs | Celery or RQ |
| Scheduler | APScheduler |
| Charts | Recharts |
| Deployment | Docker |

---

## Phase 0: Scope The First Version

### Goal

Define exactly what the first version of the project will do.

### Work To Do

- Pick the initial niche.
- Recommended niche: AI startup and tech funding news.
- Define 5 to 10 example user queries.
- Decide which web search API to use.
- Decide which LLM provider to use.
- Decide what a good final report should contain.

### Example MVP Queries

```text
Latest AI startup funding news this week
Top robotics startup news this month
Recent acquisitions in the AI industry
Funding trends in AI healthcare startups
Latest generative AI company announcements
```

### Deliverables

- Clear project scope.
- Sample queries.
- Expected report format.
- List of APIs needed.

### Done When

You can explain the MVP in one sentence:

```text
This app researches recent AI startup news, summarizes reliable sources, and generates saved market research reports.
```

---

## Phase 1: Project Setup And Repository Structure

### Goal

Create the basic project structure before building features.

### Work To Do

- Create a `frontend/` app using Next.js.
- Create a `backend/` app using FastAPI.
- Add basic environment configuration.
- Add `.env.example`.
- Add a root `README.md`.
- Add a clean folder structure for agents, workflows, services, models, and routes.
- Add a backend health check endpoint.
- Add basic linting and formatting if possible.

### Recommended Structure

```text
project/
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
  README.md
  plan.md
```

### Deliverables

- Running FastAPI backend.
- Running Next.js frontend.
- Basic project documentation.

### Done When

- `GET /health` returns a successful response.
- The frontend loads a basic page.
- The repository structure is clean and ready for feature work.

---

## Phase 2: Backend API Foundation

### Goal

Build the backend interface that the frontend and future agents will use.

### Work To Do

- Create a research request schema.
- Create a research response schema.
- Add a `POST /research` endpoint.
- Add basic error handling.
- Add logging.
- Add application settings for API keys and model configuration.
- Return a mocked research report first.

### Suggested Schemas

```text
ResearchRequest
- query
- user_id optional
- max_sources
- date_range optional

ResearchResponse
- query
- summary
- report
- sources
- generated_at
```

### Deliverables

- Backend endpoint for submitting a research query.
- Mock response that matches the final report shape.

### Done When

The frontend or an API client can send a query to the backend and receive a structured research response.

---

## Phase 3: Web Search System

### Goal

Make the backend search the web and collect relevant URLs.

### Work To Do

- Integrate one search provider.
- Recommended options: Tavily, SerpAPI, Brave Search API, or NewsAPI.
- Create a `WebSearchService`.
- Normalize search results into a common format.
- Store title, URL, snippet, source, and published date if available.
- Remove duplicate URLs.
- Add basic relevance ranking.

### Deliverables

- Search service.
- Search result schema.
- Backend can return real source links for a query.

### Done When

Given a query like:

```text
Latest AI startup funding news this week
```

The backend returns a list of relevant article URLs with titles and snippets.

---

## Phase 4: Article Extraction

### Goal

Fetch article pages and extract clean readable content.

### Work To Do

- Create a `ContentExtractionService`.
- Fetch article HTML.
- Extract article text.
- Remove navigation, ads, scripts, and unrelated content.
- Capture title, author, source, published date, and main text where possible.
- Add timeout and failure handling.
- Skip pages that cannot be extracted cleanly.

### Recommended Libraries

- `trafilatura`
- `readability-lxml`
- `beautifulsoup4`
- `httpx`

### Deliverables

- Clean article extraction pipeline.
- Extracted article schema.
- Failed extraction handling.

### Done When

The system can take URLs from the search phase and return clean article text for most valid sources.

---

## Phase 5: Summarization And Report MVP

### Goal

Generate the first real AI research report.

### Work To Do

- Summarize each article individually.
- Combine article summaries into a final report.
- Use structured LLM outputs.
- Include source citations.
- Add a final answer format.
- Make the report readable in Markdown.

### Recommended Report Sections

```text
# Research Report

## Executive Summary

## Key Findings

## Important Articles

## Emerging Trends

## Source List
```

### Deliverables

- Article-level summaries.
- Final report generation.
- Source-backed answer.

### Done When

A user can ask a research question and receive a complete Markdown report based on real web sources.

This is your first true MVP.

---

## Phase 6: Database And Research History

### Goal

Persist user queries, sources, summaries, and generated reports.

### Work To Do

- Set up PostgreSQL.
- Add SQLAlchemy or SQLModel.
- Add Alembic migrations.
- Create database tables.
- Save each research query.
- Save collected articles.
- Save generated reports.
- Add endpoints to fetch report history.

### Main Tables

```text
users
- id
- name
- email
- created_at

research_queries
- id
- user_id
- query
- created_at
- status

articles
- id
- query_id
- title
- url
- source
- published_date
- extracted_text
- summary
- created_at

reports
- id
- query_id
- title
- report_content
- generated_at

user_memory
- id
- user_id
- interest_topics
- research_history
- updated_at
```

### Deliverables

- Persistent report history.
- Database-backed research results.
- Basic history API.

### Done When

Research reports remain available after restarting the app.

---

## Phase 7: Frontend MVP

### Goal

Build the first usable interface for the research system.

### Work To Do

- Add a research query input.
- Add loading and progress states.
- Display the final report.
- Display source links.
- Add report history.
- Add a dashboard page.
- Add a detail page for saved reports.

### Core Pages

```text
/
- main research input
- recent reports

/reports
- saved report list

/reports/[id]
- full report view
- source list

/dashboard
- basic activity overview
```

### Deliverables

- Usable frontend.
- API integration.
- Saved report browsing.

### Done When

A user can run a research query from the browser, read the report, and reopen it later.

---

## Phase 8: LangGraph Workflow

### Goal

Convert the working research pipeline into a proper LangGraph workflow.

### Work To Do

- Define a shared workflow state.
- Create graph nodes for each step.
- Add edges between nodes.
- Add error and retry paths.
- Keep each node small and testable.
- Add workflow-level logging.

### Suggested Nodes

```text
plan_query
search_web
extract_content
summarize_articles
analyze_trends
generate_report
save_memory
```

### Deliverables

- LangGraph-powered research workflow.
- Explicit state transitions.
- More maintainable orchestration.

### Done When

The existing MVP still works, but the backend now uses LangGraph to coordinate the research process.

---

## Phase 9: Multi-Agent Architecture

### Goal

Split the workflow into specialized agents after the core pipeline is already reliable.

### Agents To Build

```text
Query Planner Agent
- understands intent
- breaks query into subtasks
- decides search strategy

Web Search Agent
- searches the web
- ranks relevant results
- removes duplicates

Content Extraction Agent
- fetches pages
- extracts clean text
- handles failed pages

Summarization Agent
- summarizes individual articles
- merges related findings

Trend Analysis Agent
- detects patterns
- compares categories
- identifies repeated themes

Report Generator Agent
- creates Markdown reports
- includes citations
- formats the final output

Memory Agent
- stores user preferences
- retrieves previous context
- updates research history
```

### Deliverables

- Modular agent classes.
- Tool interfaces.
- Structured agent outputs.

### Done When

Each agent has a clear responsibility and the orchestrator can run them as part of the research workflow.

---

## Phase 10: Memory And RAG

### Goal

Allow the system to use previous research and user interests when generating new reports.

### Work To Do

- Generate embeddings for article summaries and reports.
- Store embeddings in Chroma.
- Add semantic search over old reports.
- Retrieve relevant previous reports before generating a new one.
- Store user interest topics.
- Use memory to personalize report focus.

### Example Memory Behavior

```text
User often researches AI startups, funding rounds, and healthcare AI.
When a broad AI query appears, prioritize these angles in the report.
```

### Deliverables

- Vector search.
- Previous report retrieval.
- User memory retrieval.

### Done When

The system can reference older research when answering a new related query.

---

## Phase 11: Trend Analysis And Analytics

### Goal

Make the project feel like a market research product, not just a summarizer.

### Work To Do

- Extract structured data from articles.
- Track companies, sectors, funding amounts, investors, and dates.
- Identify repeated themes.
- Add simple trend scoring.
- Add frontend charts using Recharts.
- Add topic frequency charts.
- Add funding category charts where data is available.

### Example Trend Outputs

```text
AI infrastructure startups appeared in 7 of 15 collected sources.
Healthcare AI funding appeared more often than legal AI funding this week.
Several sources mention increased investor interest in AI agents.
```

### Deliverables

- Trend analysis service.
- Structured trend output.
- Analytics dashboard.

### Done When

Reports include useful patterns across multiple sources, and the dashboard visualizes those patterns.

---

## Phase 12: Background Jobs And Live Progress

### Goal

Make long-running research tasks reliable and user-friendly.

### Work To Do

- Add Redis.
- Add Celery or RQ.
- Move research execution into background jobs.
- Add job status tracking.
- Add progress updates.
- Add a live agent view in the frontend.
- Show current task, tools used, completed steps, and failed steps.

### Progress States

```text
queued
planning
searching
extracting
summarizing
analyzing
generating_report
completed
failed
```

### Deliverables

- Async research jobs.
- Job status API.
- Live progress UI.

### Done When

The user can start a research task, leave it running, and watch the system progress through each step.

---

## Phase 13: Scheduled Research

### Goal

Turn the project into an automated research assistant.

### Work To Do

- Add scheduled research topics.
- Let users choose frequency.
- Run scheduled jobs automatically.
- Save scheduled reports.
- Add schedule management UI.

### Example Feature

```text
Send me an AI startup funding report every Monday morning.
```

### Deliverables

- Scheduled research backend.
- Scheduled reports table.
- Frontend schedule management.

### Done When

The system can automatically generate reports on a recurring schedule.

---

## Phase 14: Email And Export Features

### Goal

Let users share and receive research reports outside the app.

### Work To Do

- Generate Markdown exports.
- Generate PDF exports.
- Add email provider integration.
- Recommended providers: Resend or SendGrid.
- Add email templates.
- Add a button to email or download a report.
- Connect scheduled research to email delivery.

### Deliverables

- PDF export.
- Email report delivery.
- Scheduled email reports.

### Done When

A scheduled research report can be generated, saved, and emailed automatically.

---

## Phase 15: Source Credibility And Quality Controls

### Goal

Improve trust, reliability, and recruiter impact.

### Work To Do

- Score source credibility.
- Prefer original reporting over copied summaries.
- Detect duplicate claims across sources.
- Add citation coverage checks.
- Add recency checks.
- Add low-confidence warnings.
- Add a section explaining limitations.

### Possible Scoring Factors

```text
source reputation
article recency
author availability
number of repeated claims
primary source availability
paywall or extraction quality
```

### Deliverables

- Credibility scoring.
- Better source ranking.
- Report confidence indicators.

### Done When

Reports clearly show which sources are strongest and where the system is less certain.

---

## Phase 16: Testing, Deployment, And Production Readiness

### Goal

Make the project stable enough to show publicly.

### Work To Do

- Add unit tests for services.
- Add workflow tests for LangGraph.
- Add API tests.
- Add frontend smoke tests if possible.
- Add Docker setup.
- Add production environment variables.
- Add deployment instructions.
- Add monitoring or structured logs.
- Add rate limit handling.
- Add graceful failure messages.

### Deliverables

- Test suite.
- Dockerized app.
- Deployment guide.
- Stable demo build.

### Done When

The project can be run by another developer using the README without needing your help.

---

## Phase 17: Portfolio Polish

### Goal

Make the project impressive and easy to understand for recruiters.

### Work To Do

- Improve the README.
- Add architecture diagrams.
- Add screenshots.
- Add a demo video or GIF.
- Add example reports.
- Add a technical write-up.
- Explain the LangGraph architecture.
- Explain the agent workflow.
- Explain database and memory design.
- List future improvements.

### README Sections

```text
Project Overview
Features
Architecture
Tech Stack
Agent Workflow
Database Design
How To Run Locally
Environment Variables
Example Reports
Screenshots
Future Improvements
```

### Deliverables

- Recruiter-ready README.
- Demo assets.
- Technical explanation.

### Done When

A recruiter or engineer can understand the product, architecture, and engineering value in less than five minutes.

---

## MVP Boundary

The MVP includes only these phases:

```text
Phase 0: Scope The First Version
Phase 1: Project Setup And Repository Structure
Phase 2: Backend API Foundation
Phase 3: Web Search System
Phase 4: Article Extraction
Phase 5: Summarization And Report MVP
Phase 6: Database And Research History
Phase 7: Frontend MVP
```

Do not build advanced features before the MVP works end to end.

---

## Advanced Features Boundary

After the MVP is working, add these:

```text
Phase 8: LangGraph Workflow
Phase 9: Multi-Agent Architecture
Phase 10: Memory And RAG
Phase 11: Trend Analysis And Analytics
Phase 12: Background Jobs And Live Progress
Phase 13: Scheduled Research
Phase 14: Email And Export Features
Phase 15: Source Credibility And Quality Controls
Phase 16: Testing, Deployment, And Production Readiness
Phase 17: Portfolio Polish
```

---

## Suggested Build Order Summary

1. Define the exact MVP.
2. Set up frontend and backend.
3. Create the research API.
4. Add real web search.
5. Add article extraction.
6. Add summarization.
7. Generate Markdown reports.
8. Save reports in PostgreSQL.
9. Build the frontend interface.
10. Convert the pipeline to LangGraph.
11. Split workflow into agents.
12. Add memory and RAG.
13. Add analytics and trend detection.
14. Add background jobs and progress tracking.
15. Add scheduling.
16. Add email and PDF exports.
17. Add credibility scoring.
18. Add tests, Docker, deployment, and portfolio polish.

---

## Biggest Mistakes To Avoid

- Do not build only a chatbot UI.
- Do not call the LLM directly without a workflow.
- Do not start with too many agents before the pipeline works.
- Do not skip source citations.
- Do not skip persistence.
- Do not hardcode prompts everywhere.
- Do not build scheduling before basic research works.
- Do not add analytics before reports are being saved.
- Do not build memory before you have historical data to retrieve.

---

## What Makes This Project Valuable

Most beginner AI projects are chatbots, wrappers, or UI clones.

This project is stronger because it demonstrates:

- autonomous workflows
- web-integrated AI
- planning systems
- summarization pipelines
- memory architecture
- RAG
- async backend engineering
- report generation
- production-style AI orchestration

The final result should feel like a real AI research product, not a student demo.
