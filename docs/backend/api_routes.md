# API Routes Module

**Location:** `backend/api/routes.py`

## Current Runtime Update (April 2026)

- Active backend base URL in local dev: `http://127.0.0.1:8012`
- Task analysis endpoints now use local analysis pipeline in active flow.
- OpenAI is reserved for chat assistant endpoint behavior.
- Learning endpoints available and active:
  - `POST /api/predict`
  - `POST /api/feedback`
  - `GET /api/learning-status`

## Purpose

Defines FastAPI endpoints for task analysis, weather retrieval, and activity scoring.

## Endpoints

### POST `/api/analyze-task`

Analyzes an activity description and classifies it.

**Request:**

```json
{
  "text": "playing soccer",
  "use_openai": false,
  "openai_api_key": null
}
```

**Response:** TaskAnalysisResponse with activity, classification, confidence

### POST `/api/weather`

Retrieves weather data for a location.

**Request:**

```json
{
  "city": "New York",
  "use_demo": true,
  "api_key": null
}
```

**Response:** WeatherResponse with temperature, conditions, wind, humidity

### POST `/api/analyze` (Composite)

Full analysis pipeline: task classification + weather + scoring.

**Request:**

```json
{
  "activity_text": "playing soccer",
  "city": "New York",
  "use_openai": false,
  "weather_api_key": null,
  "openai_api_key": null,
  "use_demo_weather": true
}
```

**Response:** AnalysisResponse with task, weather, sky_score, alternatives

### GET `/api/alternatives`

Suggests alternative activities.

**Request Params:**

- `classification`: "Indoor" or "Outdoor"
- `weather_city`: City for weather context
- `use_demo`: Use demo weather data

**Response:** AlternativeActivitiesResponse with suggestions[]

### GET `/api/health`

Health check endpoint.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### GET `/`

Root endpoint with documentation links.

## Response Models

### TaskAnalysisResponse

- original_text
- cleaned_text
- activity
- classification ("Indoor" | "Outdoor")
- confidence (0.0-1.0)
- reasoning
- needs_clarification
- issue (optional)
- suggested_activity (optional)
- suggestion_confidence

### WeatherResponse

- city, country, coordinates
- temperature, feels_like
- humidity, rain_1h, wind_speed
- condition, description, icon_code
- units (metric/imperial)

### AnalysisResponse

- task: TaskAnalysisResponse
- weather: WeatherResponse
- sky_score: SkyScoreResponse
- alternatives: [string]

### SkyScoreResponse

- score (0-100)
- classification
- weather_factors: [string]
- recommendations
- bonuses, penalties

## Error Handling

- 400: Task analysis failed
- 400: Weather fetch failed
- 500: Unexpected server error

## Conversion Helpers

- `convert_task_to_response()` - TaskAnalysis → API response
- `convert_weather_to_response()` - WeatherData → API response
