# 🌤️ SkyCoach AI

A sophisticated, AI-powered weather-aware activity planner that helps you schedule your week intelligently. SkyCoach automatically classifies your tasks (using OpenAI), fetches real-time weather data, and recommends the best times to do each activity based on weather suitability. Built with React, TypeScript, FastAPI, and OpenAI.

## 🔔 Current Runtime Update (April 2026)

- **Task analysis is local-first and OpenAI-free** in active app flows (`/api/analyze-task` and `/api/analyze`).
- **OpenAI is used only by chat assistant** endpoints/features.
- **Current local dev ports:** backend `127.0.0.1:8012`, frontend `127.0.0.1:5173`.
- **Inference confidence threshold:** `0.62`.
- **Context-aware suggestion handling** is enabled for typo/incomplete/ambiguous inputs.

> Note: Historical sections below still describe earlier OpenAI-first behavior for architectural background.

![SkyCoach AI](https://img.shields.io/badge/SkyCoach-AI-6366f1?style=for-the-badge&logo=cloud&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61dafb?style=for-the-badge&logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-3178c6?style=for-the-badge&logo=typescript&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge&logo=python&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991?style=for-the-badge&logo=openai&logoColor=white)

## ✨ Core Features

### 🧠 AI-Powered Task Classification

- **Two-Step OpenAI Pipeline**: Rephrases your task input for clarity, then classifies it as Indoor or Outdoor suitable
- **Intelligent Understanding**: Handles typos, abbreviations, and natural language variations seamlessly
- **Context-Aware Judgment**: Distinguishes between "work" (Indoor) and "work outside" (Outdoor)
- **Fallback Capability**: Local ML classifier trained on the activity corpus when OpenAI unavailable

### 🌍 Smart Location Detection

- **Browser Geolocation API**: Auto-detects user's GPS coordinates
- **Nominatim Reverse Geocoding**: Converts coordinates to city names automatically
- **Manual City Selection**: Override detection with manual city input
- **Location Persistence**: Saves location preference to localStorage across sessions
- **Clear/Reset Functionality**: Easy button to clear saved location and re-detect

### 🌡️ Real-Time Weather Integration

- **OpenWeatherMap API**: Live weather data (temperature, humidity, wind speed, precipitation)
- **7-Day Forecast**: Visual weather forecast for planning your entire week
- **Hourly Breakdown**: Detailed 48-hour forecast with hourly granularity
- **Dynamic Scoring**: Adjusts activity suitability scores based on weather conditions
- **Weather-Aware Recommendations**: Suggests optimal weather windows for activities

### 📅 Intelligent Task Scheduling

- **Weekly Planner**: Visualize all tasks with weather overlay for the next 7 days
- **Smart Sequencing**: Recommends best order to complete tasks based on weather suitability
- **Color-Coded Classification**: Tasks marked as Indoor (blue) or Outdoor (orange) for quick visual parsing
- **Confidence Scores**: AI provides confidence percentage for each classification

### 📋 Multi-View Organization

- **Dashboard**: Quick overview of current weather and upcoming tasks
- **Todo Manager**: Create, track, and manage your task list
- **Timetable**: Schedule tasks across days with visual time blocks
- **Planner**: Advanced weekly scheduler with weather-aware recommendations

### 🎨 Modern, Responsive UI

- **Glassmorphism Design**: Frosted glass effect cards with modern aesthetics
- **GSAP Animations**: Smooth, performant entrance and transition effects
- **Tailwind CSS**: Utility-first styling for consistent, responsive design
- **Dark Theme**: Eye-friendly dark interface with purple/blue color scheme
- **Mobile-First**: Fully responsive layouts that work on all device sizes
- **Weather Backgrounds**: Dynamic visual feedback based on current conditions

### 💾 Data Persistence

- **localStorage**: Client-side storage for user preferences and location
- **Session State**: Zustand-like hook patterns for React state management
- **Task History**: Maintains list of recent analyses for reference

## 📚 Documentation

Complete documentation is available in the `/docs` folder:

- **[System Architecture](docs/architecture/system_design.md)** - Full system design, data flow, deployment strategies, and scaling considerations

- **Backend Services:**
  - [AI Engine](docs/backend/ai_engine.md) - OpenAI integration, two-step classification pipeline, fallback mechanisms
  - [Auto-Judge](docs/backend/auto_judge.md) - Activity judgment and scoring logic
  - [Scoring Engine](docs/backend/scoring_engine.md) - Weather-based score calculation and penalty/bonus application
  - [Maps](docs/backend/maps.md) - Location visualization and geospatial features
  - [API Routes](docs/backend/api_routes.md) - Complete REST API endpoint reference with request/response schemas

- **Frontend:**
  - [Components](docs/frontend/components.md) - Detailed React component breakdown and usage patterns
  - [Services](docs/frontend/services.md) - API client, HTTP utilities, and data fetching patterns
  - [Hooks](docs/frontend/hooks.md) - Custom React hooks (usePreferredCity, useTaskStore, useApi, etc.)

- **Data Models:**
  - [Data Models](docs/datasets/data_models.md) - TypeScript/Python type definitions and schemas
  - [Activity Corpus](docs/datasets/activity_corpus.md) - Comprehensive activity dataset and classification examples

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Frontend (React + TypeScript)                    │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────────────┐    │
│  │ Activity Input  │  │  Dashboard   │  │ Planner (7-Day Calendar) │    │
│  │ (GPS + Manual)  │  │  (Overview)  │  │ (Weather + Tasks)        │    │
│  └────────┬────────┘  └──────────────┘  └──────────────────────────┘    │
│           │                              │                              │
│  ┌────────▼──────────────────────────────▼──────┐                       │
│  │     React Hooks & State Management           │                       │
│  │  • usePreferredCity (Location persistence)   │                       │
│  │  • useTaskStore (Task management)            │                       │
│  │  • useApi (API client wrapper)               │                       │
│  └────────┬─────────────────────────────────────┘                       │
│           │ HTTP/REST                                                   │
└───────────┼─────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  Backend (FastAPI + Python)                             │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    API Routes Layer                             │    │
│  │  POST /api/analyze-task    (Task classification)                │    │
│  │  POST /api/weather         (Get weather for city)               │    │
│  │  POST /api/geocode         (Reverse geocoding)                  │    │
│  └────────┬────────────────────────────────────────────────────────┘    │
│           │                                                             │
│  ┌────────▼─────────────────────────────────────────────────────────┐   │
│  │           AI Engine (Two-Step Classification)                    │   │
│  │                                                                  │   │
│  │  Step 1: Rephrase (OpenAI)                                       │   │
│  │  "washin my car" → "Washing my car"                              │   │
│  │                                                                  │   │
│  │  Step 2: Classify (OpenAI)                                       │   │
│  │  Input: "Washing my car" + Location: "New York"                  │   │
│  │  Output: { classification: "Outdoor", confidence: 0.95 }         │   │
│  │                                                                  │   │
│  │  Fallback: Local ML classifier (Decision Tree / Random Forest /  │   │
│  │              Gradient Boosting with cross-validation)            │   │
│  │  When: OpenAI key unavailable or API rate limits                 │   │
│  │  Accuracy: selected by 5-fold cross-validation on activity data  │   │
│  └────────┬─────────────────────────────────────────────────────────┘   │
│           │                                                             │
│  ┌────────▼─────────────────────────────────────────────────────────┐   │
│  │       External Services Integration                              │   │
│  │  • OpenAI GPT-4o-mini (Task classification)                      │   │
│  │  • OpenWeatherMap (Weather data & forecasts)                     │   │
│  │  • Nominatim (Reverse geocoding: coords → city name)             │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              Data Storage & Persistence                                 │
│  • Browser localStorage (user location, task preferences)               │
│  • Session State (current tasks, UI state)                              │
│  • OpenWeatherMap Cache (temporary weather data)                        │
└─────────────────────────────────────────────────────────────────────────┘
```

### OpenAI Classification Pipeline (Detailed)

#### Step 1: Task Rephrase

```
Input:  "washin my car"
Prompt: "Clean up informal language while preserving intent"
Output: "Washing my car"
```

**Purpose**: Normalize user input for more consistent classification

#### Step 2: Activity Classification

```
Input:      "Washing my car"
Context:    Location: "New York", Time: "Monday 2 PM"
Prompt:     "Is this activity better done indoors or outdoors?
             Consider weather, time of day, and location"
Output:     {
              "classification": "Outdoor",
              "reasoning": "Car washing is inherently an outdoor activity",
              "confidence": 0.95
            }
```

**Purpose**: Determine if activity is better suited for indoor or outdoor conditions

**Fallback Behavior** (when OpenAI key unavailable):

```python
Local ML classifier trained on the activity corpus:
- Decision Tree, Random Forest, and Gradient Boosting candidates
- 5-fold cross-validation to pick the best model
- Domain overrides keep clear fitness/outdoor tasks like gym as Outdoor
```

### Data Flow

1. **User Input** → ActivityInput component with GPS detection
2. **Location Resolution** → Browser Geolocation → Nominatim reverse geocoding → city name
3. **Task Submission** → POST `/api/analyze-task` with task text and location
4. **AI Classification** → Two-step OpenAI pipeline (rephrase + classify)
5. **Weather Fetch** → POST `/api/weather` to get forecast for location
6. **Task Recommendation** → Planner displays optimal scheduling based on:
   - Classification (Indoor/Outdoor)
   - Weather forecast (next 7 days)
   - User's preferred time windows
7. **Persistence** → Task saved to localStorage and displayed in Todo/Planner/Timetable views

## 📊 Decision Matrix

Weather suitability affects task scoring based on classification:

| Classification | Weather Factor     | Impact      | Details                  |
| -------------- | ------------------ | ----------- | ------------------------ |
| 🏃 **Outdoor** | Clear/Sunny        | ✅ **+30%** | Ideal conditions         |
| 🏃 **Outdoor** | Cloudy             | ✅ **+10%** | Acceptable               |
| 🏃 **Outdoor** | Light Rain         | ⚠️ **-40%** | Reduced suitability      |
| 🏃 **Outdoor** | Heavy Rain         | ❌ **-80%** | Not recommended          |
| 🏃 **Outdoor** | Wind > 15mph       | ⚠️ **-30%** | Reduced comfort          |
| 🏠 **Indoor**  | Rain/Storm         | ✅ **+20%** | Enhanced suitability     |
| 🏠 **Indoor**  | Temperature > 30°C | ✅ **+10%** | Air conditioning benefit |
| 🏠 **Indoor**  | Clear Weather      | ⚠️ **-10%** | Might prefer outdoors    |

## 🚀 Quick Start

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **OpenAI API Key** (optional for demo mode, required for full AI features)
  - Get one at [platform.openai.com](https://platform.openai.com)
- **OpenWeatherMap API Key** (optional for demo, recommended for live weather)
  - Get one at [openweathermap.org](https://openweathermap.org)

### Installation

#### 1. Clone Repository

```bash
cd "Project Ai"
```

#### 2. Backend Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install

# Create .env file for frontend configuration
# Add these optional variables:
VITE_OPENAI_MODEL=gpt-4o-mini     # Default OpenAI model
VITE_API_URL=http://localhost:8000 # Backend API address
```

### Running the Application

#### Option A: Full Stack (Recommended for Development)

**Terminal 1 - Backend:**

```bash
# From project root
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 - Frontend:**

```bash
# From frontend directory
npm run dev
```

Frontend will be available at `http://localhost:5173`
Backend API at `http://localhost:8000`

#### Option B: Using Docker Compose

```bash
# Build and run both services
docker-compose up --build

# Services will be available at:
# Frontend: http://localhost
# Backend API: http://localhost:8000
```

### Environment Variables Setup

#### Backend (.env file in root)

```env
# Required for full AI features
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_MODEL=gpt-4o-mini

# Required for weather features
OPENWEATHER_API_KEY=your-openweather-key-here

# Optional: Redis cache (for production)
REDIS_URL=redis://localhost:6379

# Optional: Logging
LOG_LEVEL=INFO
```

#### Frontend (.env.local file in frontend/)

```env
VITE_OPENAI_MODEL=gpt-4o-mini
VITE_API_URL=http://localhost:8000
```

### First Time Usage

1. **Launch** the frontend (http://localhost:5173)
2. **Enable GPS** - Click "Detect My Location" in ActivityInput to auto-detect
   - Browser will request location permission
   - City name will auto-populate
3. **Enter Activity** - Type what you want to do (typos OK!)
   - Examples: "gonna wash my car", "going to gym", "work from home"
4. **View Results** - See classification, confidence, and recommendations

### Demo Mode (No API Keys Required)

All features work in demo mode when API keys are absent:

- Task classification uses the local ML fallback classifier
- Weather shows cached/simulated data
- Location detection still works via browser geolocation

## 📝 How to Use SkyCoach AI

### Main Workflow

**1. Set Your Location**

- Click "📍 Detect My Location" to use browser geolocation (auto-detects GPS)
- Or manually enter city name in the location input field
- Your location is saved automatically for future sessions
- Click "Clear Saved Location" to reset and re-detect

**2. Add Activities to Your Todo**

- On the **Todo Page**: Click "Add New Task" and type your activity
- Examples: "wash my car", "go to gym", "work from home", "have lunch"
- Don't worry about typos or informal language - AI will understand
- Press Enter or click Add to save

**3. View in Planner (7-Day Forecast)**

- Go to the **Planner Page** to see weather-aware scheduling
- Tasks are color-coded:
  - 🔵 **Blue** = Indoor suitable activities
  - 🟠 **Orange** = Outdoor suitable activities
- Each task shows:
  - AI confidence percentage
  - Current suitability for that day
  - Weather influence on recommendation
- UI displays optimal ordering for tasks based on weather ✅

**4. Check Your Timetable**

- Navigate to **Timetable Page** for time-based scheduling
- See all tasks organized by day
- Visual calendar view with task distribution

**5. View Dashboard**

- **Dashboard Page** shows quick overview:
  - Current weather and location
  - Today's forecast
  - Upcoming tasks
  - Quick stats

### Advanced Features

**Location Management**

- Persistent across browser sessions (localStorage)
- Switch between GPS auto-detect and manual entry
- Reverse geocoding converts coordinates → city name
- Click location card to edit

**Task Analysis Details**

- View AI confidence scores for each classification
- Read the reasoning behind Indoor/Outdoor classification
- See weather factors affecting suitability:
  - Temperature changes
  - Rainfall probability
  - Wind speed impact
  - Humidity levels

**Weather Integration**

- Live 7-day forecast for your location
- Hourly breakdown available on hover
- Weather icons indicate conditions
- Temperature ranges help plan outdoor activities

**Drag & Drop Reordering** (in Todo/Timetable)

- Reorder tasks to match suggested sequence
- Drag task cards to different days
- System auto-saves changes

## 🎨 UI Features & Navigation

### Component Overview

**ActivityInput (Navigation Header)**

- Quick location selector (GPS or manual)
- City name display with edit capability
- Clear location button for reset
- Shows current location mode (Auto/Manual)

**WeatherCard**

- Current conditions for selected location
- Large temperature display
- Weather description and icons
- Wind, humidity, and UV index

**TaskCard (Planner View)**

- Task name
- Color-coded classification (Indoor/Outdoor)
- AI confidence percentage
- Suitability indicator for that day
- Weather reasoning from OpenAI

**ScoreGauge**

- Circular progress indicator with percentage
- Color changes based on suitability (Red to Green)
- Animated entrance effect (GSAP)
- Smooth transitions on value change

**WeatherBackground**

- Dynamic background changes per weather condition
- Smooth animations and transitions
- Glassmorphism effect on cards
- Responsive to weather updates

### Keyboard Shortcuts

- **Enter** - Add new task (from input field)
- **Ctrl+L** - Focus location input
- **Escape** - Close modals/dialogs

### Responsive Design

- ✅ Mobile: Single column, stacked layout
- ✅ Tablet: 2-column grid
- ✅ Desktop: 3+ column layouts
- ✅ All breakpoints tested (320px → 2560px)

### Animations & Transitions

- GSAP-powered entrance effects
- Smooth gauge filling animations
- Card hover effects (glassmorphism depth)
- Weather background transitions
- Cross-fade between views

## 📁 Project Structure

```
Project Ai/
│
├── 📄 README.md                    # This file
├── 📄 requirements.txt             # Python dependencies
├── 📄 docker-compose.yml           # Docker orchestration
├── 📄 INSTALLATION_GUIDE.md        # Detailed setup instructions
├── 📄 FULL_STACK_SETUP.md          # Full-stack deployment guide
├── 📄 QUICK_REFERENCE.md           # Quick command reference
├── 📄 AUTO_JUDGE_FEATURE.md        # Auto-judge feature documentation
├── 📄 BACKEND_API.md               # Backend API reference
│
├── 🔧 Backend (FastAPI + Python)
│   ├── backend/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI app initialization
│   │   ├── Dockerfile              # Backend containerization
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py           # API endpoints (/analyze-task, /weather, /geocode)
│   │   │
│   │   └── schemas/
│   │       ├── __init__.py
│   │       └── models.py           # Pydantic schemas (request/response models)
│   │
│   ├── services/                   # Business logic layer
│   │   ├── __init__.py
│   │   ├── ai_engine.py           # Two-step OpenAI pipeline + fallback classifier
│   │   ├── auto_judge.py          # Activity judgment logic
│   │   ├── geolocation.py         # Location handling (reverse geocoding)
│   │   └── maps.py                # Map generation utilities
│   │
│   ├── core/                      # Core functionality
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Processing pipeline orchestration
│   │   └── scoring_engine.py      # Weather-based scoring algorithm
│   │
│   ├── models/                    # Data models and classes
│   │   ├── __init__.py
│   │   └── data_classes.py        # TaskAnalysis, AnalysisRequest, etc.
│   │
│   ├── plugins/                   # Extensible plugins
│   │   ├── __init__.py
│   │   ├── normalization.py       # Input normalization
│   │   ├── quality.py             # Quality checks
│   │   └── registry.py            # Plugin registry
│   │
│   ├── themes/                    # Theme configuration
│   │   ├── __init__.py
│   │   └── styles.py              # Style definitions
│   │
│   ├── utils/                     # Utility functions
│   │   └── __init__.py
│   │
│   ├── components/               # Reusable components (Python)
│   │   ├── __init__.py
│   │   ├── animations.py          # Animation utilities
│   │   ├── cards.py               # Card components
│   │   ├── gauges.py              # Gauge components
│   │   ├── layout.py              # Layout utilities
│   │   ├── responsive.py          # Responsive design helpers
│   │   └── ui.py                  # UI utilities
│   │
│   └── tests/
│       └── test_analyze_coordinates.py  # Regression tests (10 tests)
│
├── 🎨 Frontend (React + TypeScript + Vite)
│   ├── frontend/
│   │   ├── package.json           # npm dependencies
│   │   ├── tsconfig.json          # TypeScript configuration
│   │   ├── vite.config.ts         # Vite build configuration
│   │   ├── tailwind.config.js     # Tailwind CSS setup
│   │   ├── playwright.config.ts   # E2E test configuration
│   │   ├── index.html             # HTML entry point
│   │   ├── Dockerfile             # Frontend containerization
│   │   ├── nginx.conf             # Nginx web server config
│   │   │
│   │   ├── src/
│   │   │   ├── main.tsx           # React entry point
│   │   │   ├── App.tsx            # Main App component
│   │   │   │
│   │   │   ├── components/        # Reusable React components
│   │   │   │   ├── ActivityInput.tsx      # Location + activity input form
│   │   │   │   ├── AlternativesCard.tsx   # Alternative suggestions
│   │   │   │   ├── AnalysisResult.tsx    # Classification results display
│   │   │   │   ├── AppShell.tsx          # Main app layout shell
│   │   │   │   ├── Header.tsx            # Navigation header
│   │   │   │   ├── ScoreCard.tsx         # Task score display
│   │   │   │   ├── ScoreGauge.tsx        # Animated circular gauge
│   │   │   │   ├── TaskCard.tsx          # Individual task card
│   │   │   │   ├── WeatherBackground.tsx # Dynamic weather background
│   │   │   │   ├── WeatherCard.tsx       # Weather display card
│   │   │   │   └── index.ts              # Component exports
│   │   │   │
│   │   │   ├── hooks/             # Custom React hooks
│   │   │   │   ├── useApi.ts              # API client wrapper
│   │   │   │   ├── usePreferredCity.ts   # Location persistence
│   │   │   │   └── useTaskStore.ts       # Task state management
│   │   │   │
│   │   │   ├── pages/             # Page components
│   │   │   │   ├── Dashboard.tsx         # Dashboard/home page
│   │   │   │   ├── PlannerPage.tsx       # 7-day weather planner
│   │   │   │   ├── TimetablePage.tsx     # Calendar/timeline view
│   │   │   │   └── TodoPage.tsx          # Task list management
│   │   │   │
│   │   │   ├── services/          # API and utility services
│   │   │   │   ├── api.ts                # API client configuration
│   │   │   │   └── Attached Element... (misc)
│   │   │   │
│   │   │   ├── styles/
│   │   │   │   └── globals.css           # Global styles
│   │   │   │
│   │   │   ├── types/             # TypeScript type definitions
│   │   │   │   ├── api.ts                # API response types
│   │   │   │   └── tasks.ts              # Task types
│   │   │   │
│   │   │   └── utils/             # Utility functions
│   │   │
│   │   ├── public/               # Static assets
│   │   │   └── _redirects        # Redirect rules (Netlify)
│   │   │
│   │   └── e2e/                  # End-to-end tests
│   │       └── location-auto.spec.ts    # Location detection tests
│   │
│   └── netlify.toml              # Netlify deployment config
│
└── 📖 docs/
    ├── README.md                           # Documentation index
    ├── architecture/
    │   └── system_design.md               # Full system architecture
    ├── backend/
    │   ├── ai_engine.md                  # AI pipeline detailed docs
    │   ├── auto_judge.md                 # Auto-judge feature
    │   ├── api_routes.md                 # API reference
    │   ├── maps.md                       # Maps functionality
    │   └── scoring_engine.md             # Scoring algorithm
    ├── frontend/
    │   ├── components.md                 # Component documentation
    │   ├── hooks.md                      # Hooks documentation
    │   └── services.md                   # Services documentation
    └── datasets/
        ├── data_models.md                # TypeScript/Python types
        └── activity_corpus.md            # Activity examples
```

### Key Files & Their Purposes

**Backend Core**

- `backend/main.py` - FastAPI app init, middleware setup, CORS configuration
- `backend/api/routes.py` - ALL API endpoints (analyze-task, weather, geocode)
- `services/ai_engine.py` - Two-step OpenAI pipeline, rephrase + classify, fallback rules
- `services/geolocation.py` - Nominatim integration for reverse geocoding
- `models/data_classes.py` - Pydantic models for all request/response schemas

**Frontend Core**

- `frontend/src/App.tsx` - Navigation router, main layout
- `frontend/src/hooks/usePreferredCity.ts` - Location state persistence (localStorage)
- `frontend/src/hooks/useTaskStore.ts` - Task list management
- `frontend/src/hooks/useApi.ts` - Wrapped fetch with error handling
- `frontend/src/pages/PlannerPage.tsx` - Main 7-day scheduler (OpenAI classification)
- `frontend/src/services/api.ts` - Typed API client with VITE env vars

**Configuration**

- `requirements.txt` - Python packages (FastAPI, OpenAI, requests, etc.)
- `frontend/package.json` - Node packages (React, Vite, Tailwind, etc.)
- `docker-compose.yml` - Multi-container orchestration (frontend + backend)

## ⚙️ Configuration & Environment Variables

### Backend Configuration (Root `.env` file)

```env
# ========== OPENAI CONFIGURATION ==========
# Required: Your OpenAI API key from platform.openai.com
OPENAI_API_KEY=sk-prod-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Optional: Model selection (defaults to gpt-4o-mini)
OPENAI_MODEL=gpt-4o-mini

# ========== WEATHER DATA ==========
# Required: OpenWeatherMap API key from openweathermap.org
OPENWEATHER_API_KEY=your-openweather-key-here

# ========== OPTIONAL: REDIS CACHING ==========
# For production deployments with multiple backend instances
REDIS_URL=redis://localhost:6379

# ========== LOGGING ==========
# Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL=INFO

# ========== DEPLOYMENT ==========
# Frontend URL (for CORS configuration)
FRONTEND_URL=http://localhost:5173

# API environment (development, staging, production)
ENVIRONMENT=development
```

### Frontend Configuration (frontend/.env.local)

```env
# ========== API CONFIGURATION ==========
# Backend API URL
VITE_API_URL=http://localhost:8000

# OpenAI model to use (must match backend)
VITE_OPENAI_MODEL=gpt-4o-mini

# ========== FEATURE FLAGS ==========
# Enable/disable features (optional)
VITE_ENABLE_WEATHER=true
VITE_ENABLE_FORECAST=true
VITE_ENABLE_MAPS=false
```

### Advanced Configuration

**Scoring Engine Parameters** (in `core/scoring_engine.py`):

```python
# Weather thresholds
RAIN_THRESHOLD_MM = 0.0
WIND_THRESHOLD_MPH = 15.0
HEAT_THRESHOLD_C = 30.0

# Scoring multipliers (adjustment allowed)
OUTDOOR_RAIN_PENALTY = -80           # % penalty for outdoor tasks in rain
OUTDOOR_WIND_PENALTY = -30           # % penalty for outdoor tasks in wind
INDOOR_RAIN_BONUS = +20              # % bonus for indoor tasks in rain
INDOOR_HEAT_BONUS = +10              # % bonus for indoor tasks in heat
```

**API Queue & Rate Limiting**:

- OpenAI: Default rate limits apply (40K RPM for gpt-4o-mini)
- OpenWeather: Free tier = 60 calls/min
- Nominatim: ~1-2 requests max per second

## 🛠️ Technology Stack

### Frontend

| Technology       | Version | Purpose                 |
| ---------------- | ------- | ----------------------- |
| **React**        | 18+     | UI framework            |
| **TypeScript**   | 5.3+    | Type safety             |
| **Vite**         | 5.0+    | Build tool & dev server |
| **Tailwind CSS** | 3.3+    | Utility-first styling   |
| **GSAP**         | 3.12+   | Animations              |
| **React Query**  | 4.x+    | Server state management |
| **Zustand**      | 4.x+    | Client state management |

### Backend

| Technology        | Version | Purpose           |
| ----------------- | ------- | ----------------- |
| **FastAPI**       | 0.104+  | Web framework     |
| **Python**        | 3.11+   | Runtime           |
| **Pydantic**      | 2.0+    | Data validation   |
| **OpenAI Python** | Latest  | AI classification |
| **Requests**      | 2.31+   | HTTP client       |
| **Geopy**         | 2.4+    | Reverse geocoding |
| **Uvicorn**       | 0.24+   | ASGI server       |

### DevOps & Infrastructure

| Technology         | Purpose                       |
| ------------------ | ----------------------------- |
| **Docker**         | Containerization              |
| **Docker Compose** | Multi-container orchestration |
| **Nginx**          | Reverse proxy, static serving |
| **Playwright**     | E2E testing                   |
| **Vite**           | Fast frontend builds          |

### APIs & External Services

| Service                     | Purpose                  | Pricing                            |
| --------------------------- | ------------------------ | ---------------------------------- |
| **OpenAI GPT-4o**           | Task classification      | Pay-as-you-go (~$0.00015 per task) |
| **OpenWeatherMap**          | Weather data & forecasts | Free tier available (60 calls/min) |
| **Nominatim**               | Reverse geocoding        | Free, OSM-powered                  |
| **Browser Geolocation API** | GPS coordinates          | Native browser API                 |

## 🔌 API Endpoints Reference

### Task Analysis

```
POST /api/analyze-task

Request:
{
  "text": "going to gym",
  "location": "New York",
  "use_openai": true,
  "openai_api_key": "sk-...",
  "openai_model": "gpt-4o-mini"
}

Response:
{
  "classification": "Outdoor",
  "reasoning": "Going to gym is typically an outdoor activity due to...",
  "confidence": 0.92,
  "original_text": "going to gym",
  "processed_text": "Going to gym"
}
```

### Weather Data

```
POST /api/weather?city=New+York

Response:
{
  "city": "New York",
  "temperature": 22.5,
  "condition": "Partly Cloudy",
  "humidity": 65,
  "wind_speed": 12.5,
  "forecast": [
    {
      "dt": 1685836800,
      "temp_max": 24.2,
      "temp_min": 19.1,
      "condition": "Sunny"
    },
    ...
  ]
}
```

### Geocoding

```
POST /api/geocode

Request:
{
  "latitude": 40.7128,
  "longitude": -74.0060
}

Response:
{
  "city": "New York",
  "country": "United States",
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

For full API documentation, see [BACKEND_API.md](BACKEND_API.md)

## 🧪 Testing

### Backend Tests

Run Python regression tests:

```bash
# From project root
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_analyze_coordinates.py -v

# Run with coverage
python -m pytest tests/ --cov=services --cov=core
```

**Current Test Coverage:**

- ✅ 10 regression tests for classification behavior
- ✅ Tests validate: gym→Outdoor, work→Indoor, work outside→Outdoor
- ✅ Tests use the local ML fallback classifier (no API key required)
- ✅ Tests verify OpenAI pipeline with mock responses
- 📌 Location detection tested via e2e (Playwright)

### Frontend Tests

Run E2E tests with Playwright:

```bash
# Install browsers (first time only)
npx playwright install

# Run e2e tests
npm run test:e2e

# Run specific test
npx playwright test location-auto.spec.ts

# Run with UI
npx playwright test --ui

# Debug mode
npx playwright test --debug
```

**Current E2E Test Coverage:**

- ✅ Location auto-detection flow
- ✅ Manual location entry
- ✅ Task classification
- ✅ Navigation between pages

### Type Checking

```bash
# TypeScript type checking
cd frontend && npm run type-check

# Backend type checking (optional mypy)
mypy backend/ services/
```

## 🐛 Troubleshooting

### "OpenAI API key is required when use_openai=True"

**Problem:** Classification feature not working
**Solution:**

1. Set `OPENAI_API_KEY` in your `.env` file
2. Restart backend: `Stop-Process -Name python` then restart uvicorn
3. Ensure frontend sends `use_openai=true` in request

### "Failed to fetch weather data"

**Problem:** Weather not showing for location
**Solution:**

1. Verify `OPENWEATHER_API_KEY` in `.env`
2. Check that city name is valid (use geolocation API to verify)
3. Try different city: "New York" instead of "ny"
4. Check OpenWeather rate limits (60/min on free tier)

### "Location permission denied"

**Problem:** Browser geolocation not working
**Solution:**

1. Check browser permissions (Settings → Privacy → Location)
2. Ensure site is accessed over HTTPS (required for geolocation)
3. Clear browser cache and refresh page
4. Manually enter city name as fallback
5. Check browser console for specific errors

### "Backend not responding (CORS error)"

**Problem:** Frontend can't reach backend API
**Solution:**

1. Verify backend is running: `http://localhost:8000/docs`
2. Check VITE_API_URL in `frontend/.env.local`
3. Ensure FRONTEND_URL in backend `.env` matches frontend URL
4. Clear browser cache + hard refresh (Ctrl+Shift+R)
5. Check browser console for exact error message

### "Tasks not saving to localStorage"

**Problem:** Tasks disappear after refresh
**Solution:**

1. Check browser localStorage is enabled
2. Verify browser isn't in private/incognito mode (disables localStorage)
3. Check browser storage quota (DevTools → Application → Storage)
4. Clear other extensions that might interfere
5. Try different browser to isolate issue

### "Classification always says "Indoor" or "Outdoor""

**Problem:** AI classifier not differentiating tasks properly
**Solution:**

1. Ensure OpenAI API key is set and working
2. Check backend logs: `tail -f <backend_log_file>`
3. Try simpler task names: "gym" instead of "gonna go to the gym later"
4. Verify fallback classifier logic in `services/ai_engine.py`
5. Test API directly: `curl -X POST http://localhost:8000/api/analyze-task -d '{"text":"gym"}'`

### "Frontend build fails with TypeScript errors"

**Problem:** `npm run build` exits with errors
**Solution:**

1. Check TypeScript errors: `npm run type-check`
2. Update dependencies: `npm install`
3. Clear cache: `rm -rf node_modules package-lock.json && npm install`
4. Check for circular imports in components/
5. Verify all imports match actual file paths

### "Port 8000 already in use"

**Problem:** Backend fails to start
**Solution:**

```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (Windows PowerShell)
Stop-Process -Id <PID> -Force

# Or use different port
python -m uvicorn backend.main:app --port 8001
```

## 🚀 Deployment

### Docker Deployment

```bash
# Build images
docker-compose build

# Run services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production Considerations

1. **Security**
   - Use environment variables for all secrets (never hardcode)
   - Enable HTTPS/SSL in Nginx configuration
   - Set strong CORS origins (`FRONTEND_URL` in backend `.env`)
   - Rate limit API endpoints
   - Validate all user inputs

2. **Performance**
   - Enable Redis caching for weather data (set `REDIS_URL`)
   - Use CDN for static frontend assets
   - Implement request queueing for OpenAI calls
   - Monitor API rate limits
   - Cache geocoding results

3. **Monitoring**
   - Use application performance monitoring (APM)
   - Log all API errors and exceptions
   - Monitor OpenAI API usage and costs
   - Track frontend performance (load times)
   - Set up alerts for service failures

4. **Database** (Future Enhancement)
   - Consider adding PostgreSQL for task history
   - Implement user accounts and authentication
   - Store location preferences per user
   - Track usage statistics

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**

   ```bash
   # On GitHub, click "Fork"
   ```

2. **Create a feature branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation

4. **Testing before commit**

   ```bash
   # Backend tests
   python -m pytest tests/ -v

   # Frontend tests
   npm run test:e2e

   # Type checking
   npm run type-check
   mypy backend/
   ```

5. **Commit with clear messages**

   ```bash
   git commit -m "feat: add new feature description"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

### Code Style

- **Python**: Follow PEP 8 (Black formatter)
- **TypeScript**: Follow ESLint rules in config
- **Comments**: Add comments for complex logic
- **Naming**: Use clear, descriptive names

### Feature Ideas

- [ ] User authentication & multi-user support
- [ ] Task history and analytics dashboard
- [ ] Advanced filtering (by date, category, etc.)
- [ ] Mobile app (React Native)
- [ ] Calendar integration (Google Calendar, Outlook)
- [ ] Weather alerts and notifications
- [ ] Task categories/tags system
- [ ] Collaborative task planning (shared locations)
- [ ] Export to calendar formats (ICS, etc.)
- [ ] AI-powered smart suggestions

## 📊 Performance & Optimization

### Frontend

- **Bundle Size**: ~150KB gzipped (React + Tailwind + GSAP)
- **Page Load Time**: < 2s on 4G
- **Time to Interactive**: < 3s
- **Lighthouse Score**: 85+ (on desktop)

**Optimization Strategies:**

- Code splitting by page
- Image compression and WebP support
- Service Worker for offline capability
- Lazy loading of components
- Memoization of expensive calculations

### Backend

- **API Response Time**: < 500ms for classify (with OpenAI)
- **Weather Fetch**: < 1s (OpenWeatherMap API)
- **Geocoding**: < 500ms (Nominatim)
- **Fallback Classifier**: Fast local ML inference after model training

**Optimization Strategies:**

- Cache weather data for 1 hour
- Batch geolocation requests
- Connection pooling for external APIs
- Async task processing
- Database indexing (future)

## 📈 Roadmap

### Phase 1 - Core (Complete ✅)

- [x] OpenAI task classification
- [x] Location detection & persistence
- [x] Weather integration
- [x] 7-day planner view
- [x] Responsive UI
- [x] Docker deployment

### Phase 2 - Enhancement (In Progress 🚀)

- [ ] User authentication
- [ ] Task history & analytics
- [ ] Advanced filtering
- [ ] Notification system
- [ ] Calendar sync

### Phase 3 - Advanced (Future 🎯)

- [ ] Mobile app
- [ ] AI-powered insights
- [ ] Collaborative planning
- [ ] Activity recommendations based on habit
- [ ] Integration with fitness trackers

## 📞 Support & Contact

- **Documentation**: See `/docs` folder
- **Issues**: Create GitHub issue for bugs
- **Discussions**: Use GitHub Discussions for questions
- **Email**: [Add contact email if applicable]

## 📄 License

MIT License - Feel free to use and modify for any purpose!

```
MIT License

Copyright (c) 2024 SkyCoach AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<div align="center">

### 🌤️ Built with ❤️ using React, FastAPI, and OpenAI

**Let the weather guide your day!**

[⭐ Star on GitHub](https://github.com/YoRu-Cat/SkyCoach-Ai) • [📖 Read Docs](docs/README.md) • [🐛 Report Issues](https://github.com/YoRu-Cat/SkyCoach-Ai/issues)

[Back to Top](#-skycoach-ai)

</div>
