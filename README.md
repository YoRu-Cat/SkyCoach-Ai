# SkyCoach AI

SkyCoach AI is a weather-aware activity planner with a FastAPI backend and a React frontend.

## Current Architecture

- Task analysis is local-model driven in active API flows.
- OpenAI is reserved for chat assistant flow only.
- Weather and scoring remain backend services in the full analysis pipeline.
- Auto-judge provides context-aware suggestions for incomplete or ambiguous activity input.

## Runtime Defaults (Local Dev)

- Backend: http://127.0.0.1:8012
- Backend docs: http://127.0.0.1:8012/docs
- Frontend: http://127.0.0.1:5173/index.html
- Inference confidence threshold: 0.62

## Main Features

### Task Analysis

- Local ML inference via the unified `ml_system`
- Context-aware normalization and suggestion generation
- Clarification handling for low-confidence input

### Weather and Scoring

- Live or demo weather retrieval
- Sky score computation from activity plus weather
- Alternative activity suggestions based on conditions

### Frontend Experience

- React + TypeScript UI
- Planner, dashboard, timetable, and todo views
- API-driven task analysis with suggestion rendering

## API Surface (Backend)

- `POST /api/analyze-task`
- `POST /api/weather`
- `POST /api/score`
- `POST /api/analyze`
- `GET /api/alternatives`
- `GET /api/health`
- `POST /api/predict`
- `POST /api/feedback`
- `GET /api/learning-status`
- `POST /api/chat-assistant`

## Quick Start

### 1) Install dependencies

```powershell
cd "e:\Java\Project\Project Ai"
pip install -r requirements.txt
```

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
```

### 2) Start backend

```powershell
cd "e:\Java\Project\Project Ai"
E:/Anaconda/Installed/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

### 3) Start frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

### 4) Open app

- http://127.0.0.1:5173/index.html
- http://127.0.0.1:8012/docs

## Environment

Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8012
```

Optional backend environment variables:

- `OPENWEATHER_API_KEY` for live weather
- `OPENAI_API_KEY` for chat assistant flow

## Repository Documentation

- `docs/README.md`
- `docs/architecture/system_design.md`
- `docs/architecture/deep_dive.md`
- `docs/backend/api_routes.md`
- `docs/backend/ai_engine.md`
- `docs/architecture/ml_system/overview.md`
- `docs/architecture/ml_system/integration.md`
- `docs/architecture/ml_system/training_and_data.md`
- `docs/architecture/ml_system/quick_reference.md`
