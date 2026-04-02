# Frontend Services

**Location:** `frontend/src/services/`

## API Service Module

**File:** `api.ts`

### Purpose
Axios client configuration and API endpoint functions for backend communication.

### Configuration

**API Base URL Logic:**
1. If running on Netlify (netlify.app domain) → use same-origin `/api` (proxied)
2. Else if VITE_API_URL env var set → use that
3. Else if production build → use Render backend URL
4. Else → use localhost:8000 (dev)

**Axios Client Setup:**
```javascript
baseURL: `${API_BASE_URL}/api`
headers: { "Content-Type": "application/json" }
```

### API Functions

#### `analyzeTask(text: string)`
Analyze activity description.
- **Endpoint:** POST `/analyze-task`
- **Input:** Activity text
- **Output:** TaskAnalysis
- **Parameters:** use_openai=false, openai_api_key=null

#### `getWeather(city: string)`
Get weather for a city.
- **Endpoint:** POST `/weather`
- **Input:** City name
- **Output:** WeatherData
- **Parameters:** use_demo=true, api_key=null

#### `fullAnalysis(activityText, city)`
Complete analysis pipeline.
- **Endpoint:** POST `/analyze`
- **Input:** Activity text, city
- **Output:** AnalysisResponse (task, weather, score, alternatives)
- **Parameters:** All demo/automatic settings

#### `getAlternatives(classification)`
Get alternative activity suggestions.
- **Endpoint:** GET `/alternatives`
- **Input:** Classification ("Indoor" or "Outdoor")
- **Output:** Array of suggestion strings

#### `healthCheck()`
Check if API is healthy.
- **Endpoint:** GET `/health`
- **Output:** Boolean (true if healthy)
- **Error Handling:** Returns false on any error

### Error Handling
- All functions return Promise
- healthCheck catches errors and returns false
- Others propagate errors to callers

### Type Imports
- `TaskAnalysis, WeatherData, AnalysisResponse` from `@app-types/api`

### Exports
- `API_BASE_URL` - Current API base URL (used in error screens)
