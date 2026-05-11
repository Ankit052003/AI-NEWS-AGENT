# Phase 1: Project Setup And Repository Structure

Phase 1 creates the skeleton that every later feature will plug into. The goal is not to build the research engine yet. The goal is to make sure the frontend, backend, configuration, and folders are ready.

## What Exists Now

- `frontend/` is a Next.js app with a basic research workspace page.
- `backend/` is a FastAPI app with a `/health` route.
- `.env.example` documents the first environment variables.
- Backend folders are prepared for future agents, workflows, RAG, memory, routes, schemas, services, models, and utilities.
- Frontend folders are prepared for components, hooks, services, and styles.
- `.gitignore` keeps local dependencies, caches, and secrets out of git.
- Backend Ruff config is available in `backend/pyproject.toml`.

## Why This Structure Matters

The project will grow phase by phase:

- routes expose API endpoints
- schemas define request and response shapes
- services hold reusable business logic
- workflows will coordinate the research pipeline
- agents will be added later, after the simple pipeline works
- memory and RAG folders are ready for later persistence and retrieval features

Keeping these boundaries early makes Phase 2 easier because the first research endpoint can go into `backend/app/routes/`, with its request and response models in `backend/app/schemas/`.

## Verify Phase 1

Run the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Check the health endpoint:

```text
GET http://localhost:8000/health
```

Expected response shape:

```json
{
  "status": "ok",
  "service": "News Research Agent",
  "environment": "development"
}
```

Run the frontend:

```powershell
cd frontend
npm install
npm run dev
```

If PowerShell blocks `npm.ps1`, use:

```powershell
npm.cmd install
npm.cmd run dev
```

Open:

```text
http://localhost:3000
```

## Done Criteria

- FastAPI app starts successfully.
- `GET /health` returns `status: ok`.
- Next.js app loads a basic page.
- Repository structure matches the project plan and is ready for Phase 2.
