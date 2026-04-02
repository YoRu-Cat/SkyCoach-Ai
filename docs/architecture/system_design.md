# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     SkyCoach AI System                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────┐         ┌──────────────────────────────────┐
│   React Frontend    │         │     FastAPI Backend              │
│  (Vite + TypeScript)│         │   (Python 3.11)                  │
├─────────────────────┤         ├──────────────────────────────────┤
│ - ActivityInput     │◄──────► │ - Task Analysis Engine           │
│ - ScoreGauge        │  HTTPS/ │ - Auto-Judge (fuzzy matching)    │
│ - WeatherCard       │   JSON  │ - Scoring Engine (decision matrix)│
│ - AnalysisResult    │         │ - Weather Integration            │
│ - WeatherBackground │         │ - Map Rendering                  │
└─────────────────────┘         └──────────────────────────────────┘
        │                                  │
        │                                  │
        ▼                                  ▼
┌────────────────────────────────────────────────────────────────┐
│                    External APIs                               │
├────────────────────────────────────────────────────────────────┤
│ - OpenAI (GPT-4o-mini) for LLM-based task analysis            │
│ - OpenWeatherMap for real weather data                        │
│ - OpenStreetMap/Folium for interactive maps                  │
└────────────────────────────────────────────────────────────────┘
```

## Request-Response Flow

```
┌──────┐
│ User │
└──┬───┘
   │
   ▼
┌─────────────────────────────────────────┐
│ 1. Activity Input Form                  │
│    - Activity description text          │
│    - Location (city)                    │
└─────────────┬───────────────────────────┘
              │
              ▼
         ┌────────────────────┐
         │ POST /api/analyze  │
         └────────┬───────────┘
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
   ┌─────────────────────────────────────────┐
   │ Backend Analysis Pipeline               │
   ├─────────────────────────────────────────┤
   │ 1. Tokenize & keyword match             │
   │ 2. Classify (Indoor/Outdoor)            │
   │ 3. Apply auto-judge (if needed)         │
   │ 4. Fetch weather for city               │
   │ 5. Calculate SkyScore                   │
   │ 6. Generate recommendations             │
   └────────────┬────────────────────────────┘
                │
                ▼
    ┌─────────────────────────────────┐
    │ JSON Response                   │
    │ - Task analysis                 │
    │ - Weather data                  │
    │ - SkyScore (0-100)              │
    │ - Alternative suggestions       │
    └────────┬────────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │ 2. Frontend Rendering            │
    │ - TaskCard                       │
    │ - WeatherCard + Map              │
    │ - ScoreGauge (animated)          │
    │ - AlternativesCard with buttons  │
    └──────────┬───────────────────────┘
               │
               ▼
            ┌──────┐
            │ User │
            └──────┘
```

## Component Relationships

### Backend Services

```
services/ai_engine.py
├── analyze_task_openai() → TaskAnalysis
├── analyze_task_fallback() → TaskAnalysis
├── get_weather() → WeatherData
└── Helper functions (_count_keyword_matches, etc.)

services/auto_judge.py
├── ACTIVITY_CORPUS (100+ activities)
├── suggest_activity() → (activity, confidence, classification)
└── auto_judge_input() → suggestion dict

core/scoring_engine.py
├── calculate_sky_score() → SkyScoreResult
├── decision matrix (rain/wind/temp penalties)
└── get_alternative_activities() → [(emoji, description)]

services/maps.py
└── render_map() → folium.Map (interactive)

backend/api/routes.py
├── /analyze-task POST
├── /weather POST
├── /analyze POST (composite)
├── /alternatives GET
├── /health GET
└── / GET (root)
```

### Frontend Components

```
App.tsx
├── Query client setup
├── Health check gate
└── Dashboard

Dashboard.tsx
├── WeatherBackground (animated)
├── Header
├── ActivityInput (left panel)
└── AnalysisResult (right panel)
    ├── TaskCard
    ├── WeatherCard (+ map)
    ├── ScoreCard
    └── AlternativesCard

Animations (via GSAP)
├── Dashboard layout entrance
├── ScoreGauge needle sweep
├── AnalysisResult panel stagger
└── WeatherBackground orbits
```

## Data Models

```
TaskAnalysis
├── activity: str
├── classification: "Indoor" | "Outdoor"
├── confidence: 0.0-1.0
├── needs_clarification: bool
└── suggested_activity: str (optional)

WeatherData
├── city, country, coordinates
├── temperature, humidity
├── rain_1h, is_raining
├── wind_speed, wind_mph
├── condition (Clear/Rain/Snow/etc)
└── description

SkyScoreResult
├── score: 0-100
├── weather_factors: [str]
├── bonuses: [(name, value, description)]
├── penalties: [(name, value, description)]
└── recommendation: str
```

## Deployment Architecture

```
Netlify (Frontend)                  Render (Backend)
├── React SPA at root               ├── FastAPI server
├── /api/* proxy redirect           ├── Port 8000
│   └─► Render backend              ├── Environment vars:
├── dist/ folder deployed           │   - ALLOWED_ORIGINS
└── Client-side routing             │   - ALLOWED_ORIGIN_REGEX
                                    └── Python 3.11 runtime

Communication:
Browser ──HTTPS──► Netlify /api redirect ──HTTPS──► Render
         No CORS issues (server-side proxy)
```

## Decision Matrix (Scoring)

```
Activity: Indoor
├── Rain detected         → +20 bonus
├── Hot (>30°C)          → +10 bonus
└── Otherwise            → Base 100

Activity: Outdoor
├── Rain detected        → -80 penalty
├── High wind (>15mph)   → -30 penalty
├── Otherwise            → Base 100
└── Final score: 0-100
```

## Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite (build tool)
- TailwindCSS (styling)
- GSAP (animations)
- Axios (HTTP)
- React Query (state management)

**Backend:**
- FastAPI (framework)
- Pydantic (validation)
- OpenAI API (LLM)
- OpenWeatherMap API (weather)
- Folium (maps)
- geopy (geocoding)

**Deployment:**
- Docker (containerization)
- Netlify (frontend hosting)
- Render (backend hosting)
- nginx (web server, SPA routing)
