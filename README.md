# SkyCoach AI

SkyCoach AI is a weather-aware task planning system with a FastAPI backend, React frontend, ML-based task classification, and a reminder-driven Todo workflow.

## Runtime Defaults

- Backend API: <http://127.0.0.1:8012>
- Backend docs: <http://127.0.0.1:8012/docs>
- Frontend: <http://127.0.0.1:5173/index.html>
- Local inference confidence threshold: 0.62

## System Overview

```mermaid
flowchart LR
  UI[React Frontend] --> API[FastAPI Routes]
  API --> Analyze[Task Analysis Engine]
  Analyze --> ML[Unified ML System]
  Analyze --> Judge[Auto Judge + Dictionary + Token Semantics]
  API --> Weather[Weather Service Demo or OpenWeather]
  API --> Score[Scoring Engine]
  Score --> Alt[Alternative Activities]
  UI --> Store[Task Store + Reminder Scheduler]
  Store --> Browser[Notification + Vibration + Ringtone]
```

## End-to-End Analysis Flow

```mermaid
sequenceDiagram
  participant F as Frontend
  participant R as API /api/analyze
  participant A as analyze_task_smart
  participant W as Weather Layer
  participant S as Scoring Engine

  F->>R: activity_text + city or coordinates
  R->>A: analyze_task_smart(text, use_openai, key, model)
  A-->>R: TaskAnalysis
  R->>W: demo/live weather + forecast
  W-->>R: WeatherData + forecast_slots
  R->>S: calculate_sky_score + recommend_best_schedule
  S-->>R: score_result + best time/date
  R-->>F: task + weather + score_result + alternatives
```

## Feature Set

### Task Intelligence

- Hybrid local analysis combining ML, dictionary, and token semantics.
- Optional OpenAI path when enabled per request and key is present.
- Clarification and suggestion fields for ambiguous user input.

### Planner and Scoring

- Live or deterministic demo weather.
- Coordinate-aware weather lookup.
- Weather-based score plus alternatives and best schedule recommendation.

### Todo and Timetable UX

- One-week timetable scheduling with conflict-aware slot handling.
- Reminder engine with browser notifications, vibration, and ringtone presets.
- Due-time Activity Check workflow:
  - Yes, completed: remove completed due task.
  - No, reschedule: move to next best available slot.

## API Surface

- POST /api/analyze-task
- POST /api/weather
- POST /api/score
- POST /api/analyze
- GET /api/alternatives
- GET /api/health
- POST /api/predict
- POST /api/feedback
- GET /api/learning-status
- POST /api/chat-assistant
- POST /api/backend-cli

## Quick Start

### 1) Install dependencies

```powershell
cd "e:\Java\Project\Project Ai"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
```

### 2) Run backend

```powershell
cd "e:\Java\Project\Project Ai"
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

### 3) Run frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

### 4) Open app

- <http://127.0.0.1:5173/index.html>
- <http://127.0.0.1:8012/docs>

## Tests

Use the root backend test runner:

```powershell
cd "e:\Java\Project\Project Ai"
.\run_backend_tests.cmd
```

## Environment

Create frontend/.env.local:

```env
VITE_API_URL=http://127.0.0.1:8012
```

Optional backend variables:

- OPENWEATHER_API_KEY
- OPENAI_API_KEY
- OPENAI_MODEL

## Documentation Index

- docs/README.md
- docs/architecture/system_design.md
- docs/backend/api_routes.md
- docs/backend/ai_engine.md
- docs/frontend/components.md
- docs/frontend/hooks.md
- docs/frontend/services.md
