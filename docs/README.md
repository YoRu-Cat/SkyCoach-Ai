# SkyCoach AI Documentation

Complete reference documentation for the SkyCoach AI system.

## 📖 Documentation Index

### [🏗️ Architecture](architecture/system_design.md)

System design, deployment architecture, request-response flow, component relationships, decision matrices, and technology stack.

#### [🤖 ML System Overview](architecture/ml_system/overview.md)

Component-based ML architecture overview for training, inference, and continuous learning.

#### [🧩 ML System Integration](architecture/ml_system/integration.md)

Step-by-step backend integration guide for the unified `ml_system` API.

#### [⚡ ML System Quick Reference](architecture/ml_system/quick_reference.md)

Fast operational reference for setup, common API calls, and troubleshooting.

### Backend Services

#### [🧠 AI Engine](backend/ai_engine.md)

Task analysis and activity classification using OpenAI integration or keyword matching fallback. Includes auto-judgment for incomplete inputs.

**Key Functions:**

- `analyze_task_openai()` - LLM-based task analysis
- `analyze_task_fallback()` - Keyword-based classification
- `get_weather()` - Fetch weather from OpenWeatherMap
- `get_demo_weather()` - Demo weather data

#### [🎯 Auto-Judge Module](backend/auto_judge.md)

Fuzzy matching engine for suggesting activities from incomplete/broken input. Contains 100+ activity corpus across Indoor/Outdoor categories.

**Key Functions:**

- `suggest_activity()` - Fuzzy match incomplete input
- `auto_judge_input()` - Main entry point

#### [📊 Scoring Engine](backend/scoring_engine.md)

Decision matrix-based SkyScore calculation (0-100) based on activity type and weather conditions. Generates alternative suggestions.

**Key Functions:**

- `calculate_sky_score()` - Compute activity suitability score
- `get_alternative_activities()` - Suggest alternatives

#### [🗺️ Maps Module](backend/maps.md)

Interactive Folium map rendering with weather overlays, intensity visualization, and multi-layer support.

**Key Functions:**

- `render_map()` - Create interactive map with weather

#### [📡 API Routes](backend/api_routes.md)

FastAPI REST endpoints for task analysis, weather retrieval, scoring, and alternatives.

**Endpoints:**

- POST `/api/analyze-task` - Analyze activity
- POST `/api/weather` - Get weather
- POST `/api/analyze` - Full analysis pipeline
- GET `/api/alternatives` - Get suggestions
- GET `/api/health` - Health check

### Frontend Components

#### [🎛️ Components](frontend/components.md)

Complete overview of all React components with props, features, styling, and animations.

**Components:**

- ActivityInput - Form for activity & location
- TaskCard - Analysis display
- WeatherCard - Weather & map
- ScoreCard - Score breakdown
- ScoreGauge - Animated gauge
- AlternativesCard - Suggestions
- WeatherBackground - Animated background
- AnalysisResult - Results container
- Header - Navigation

#### [🔌 Services](frontend/services.md)

API client configuration with Netlify runtime detection and multi-layered fallback strategy.

**Key Functions:**

- `analyzeTask()` - Send task for analysis
- `getWeather()` - Fetch weather
- `fullAnalysis()` - Complete pipeline
- `getAlternatives()` - Get suggestions
- `healthCheck()` - API status

#### [🪝 Hooks](frontend/hooks.md)

Custom React hooks for data fetching and state management.

**Hooks:**

- `useFullAnalysis()` - React Query mutation for analysis

### Data & Models

#### [💾 Data Models](datasets/data_models.md)

Comprehensive reference for all dataclasses, type definitions, and schemas.

**Models:**

- Config - Configuration parameters
- TaskAnalysis - Analysis result
- WeatherData - Weather information
- SkyScoreResult - Scoring result
- HistoryEntry - Saved analysis

#### [🎯 Activity Corpus](datasets/activity_corpus.md)

100+ activity dataset organized by indoor/outdoor classification. Includes matching algorithm details.

**Dataset Size:** 50+ Outdoor, 50+ Indoor activities

---

## 🚀 Quick Links

- **Main Project:** [README.md](../README.md)
- **Frontend:** [frontend/](../frontend/)
- **Backend:** [backend/](../backend/)
- **Services:** [services/](../services/)
- **Core Logic:** [core/](../core/)

## 📝 File Organization

```
/docs/
├── README.md (this file)
├── architecture/
│   ├── system_design.md
│   └── ml_system/
│       ├── overview.md
│       ├── integration.md
│       └── quick_reference.md
├── backend/
│   ├── ai_engine.md
│   ├── auto_judge.md
│   ├── scoring_engine.md
│   ├── maps.md
│   └── api_routes.md
├── frontend/
│   ├── components.md
│   ├── services.md
│   └── hooks.md
└── datasets/
    ├── data_models.md
    └── activity_corpus.md
```

## 🔍 Finding Information

**Looking for...?**

- **How to deploy** → [system_design.md](architecture/system_design.md)
- **Component details** → [components.md](frontend/components.md)
- **API endpoints** → [api_routes.md](backend/api_routes.md)
- **Task classification logic** → [ai_engine.md](backend/ai_engine.md)
- **Scoring algorithm** → [scoring_engine.md](backend/scoring_engine.md)
- **Activity suggestions** → [auto_judge.md](backend/auto_judge.md)
- **Data types** → [data_models.md](datasets/data_models.md)
- **Available activities** → [activity_corpus.md](datasets/activity_corpus.md)
