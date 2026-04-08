"""
API Endpoint Documentation and Testing Guide

## Current Runtime Update (April 2026)

- Active backend URL: `http://127.0.0.1:8012`
- Active docs URL: `http://127.0.0.1:8012/docs`
- Task analysis routes (`/api/analyze-task`, `/api/analyze`) now run local analysis pipeline.
- OpenAI is reserved for chat assistant flows only.
- Inference confidence threshold in current model runtime: `0.62`.

## Running the Backend API

Start the backend server with:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the interactive API docs at: http://localhost:8000/docs

## Endpoints

### 1. Health Check

GET /api/health

Response:
{
"status": "healthy",
"service": "SkyCoach API",
"version": "1.0.0"
}

### 2. Analyze Task

POST /api/analyze-task

Request:
{
"text": "playing soccer",
"use_openai": false,
"openai_api_key": null
}

Response:
{
"original_text": "playing soccer",
"cleaned_text": "Playing Soccer",
"activity": "needs clarification or activity name",
"classification": "Indoor" or "Outdoor",
"confidence": 0.67,
"reasoning": "Classification reasoning",
"needs_clarification": false,
"issue": null or "issue description"
}

### 3. Get Weather

POST /api/weather

Request:
{
"city": "New York",
"latitude": null,
"longitude": null,
"api_key": null,
"use_demo": true
}

Response:
{
"city": "New York",
"country": "US",
"latitude": 40.7128,
"longitude": -74.006,
"temperature": 18.0,
"feels_like": 16.0,
"humidity": 51,
"rain_1h": 0.0,
"is_raining": false,
"wind_speed": 9.0,
"wind_mph": 20.1,
"condition": "Clouds",
"description": "scattered clouds",
"icon_code": "03d",
"units": "metric",
"temp_unit": "°C"
}

### 4. Calculate SkyScore

POST /api/score

Request body requires task and weather objects (see TaskAnalysisResponse and WeatherResponse schemas)

### 5. Get Alternatives

GET /api/alternatives?classification=Outdoor&weather_city=New York&use_demo=true

Response:
{
"suggestions": ["cycling", "hiking", "playing sports"],
"reason": "Based on outdoor activity and weather conditions"
}

### 6. Full Analysis Pipeline

POST /api/analyze

Combined request-response that chains all services together:
task analysis → weather fetch → sky score calculation → alternatives

## Status

✓ API endpoints created and tested
✓ All 5 core endpoints functional (analyze-task, weather, score, alternatives, analyze)
✓ Health check working
✓ FastAPI app initialization successful
✓ CORS middleware configured for Streamlit (8501), React (3000), and other localhost ports
✓ Pydantic validation working

## Verified Behavior

- "washing car" → Outdoor classification, confidence 0.67 ✓
- incomplete inputs trigger needs_clarification flag ✓
- Demo weather returns consistent data
- API serves responses in <500ms
  """
