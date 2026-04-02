# Data Models and Types

**Location:** `models/data_classes.py` and `frontend/src/types/`

## Backend Models (Python)

### Config

Central configuration dataclass.

- `openai_api_key` - Optional OpenAI key
- `openweather_api_key` - Optional weather API key
- `openai_model` - Model name (default: "gpt-4o-mini")
- `weather_units` - "metric" or "imperial"
- `rain_threshold` - Minimum rain (mm) to trigger penalty (default: 0.0)
- `wind_threshold_mph` - Wind speed threshold (default: 15.0 mph)
- `heat_threshold_c` - Temperature threshold (default: 30.0°C)
- `outdoor_rain_penalty` - Score adjustment (default: -80)
- `outdoor_wind_penalty` - Score adjustment (default: -30)
- `indoor_rain_bonus` - Score adjustment (default: +20)
- `indoor_heat_bonus` - Score adjustment (default: +10)

### TaskAnalysis

Result of activity analysis.

- `original_text` - User input
- `cleaned_text` - Cleaned/corrected text
- `activity` - Identified activity name
- `classification` - "Indoor" or "Outdoor"
- `confidence` - Confidence score (0.0-1.0)
- `reasoning` - Explanation of classification
- `needs_clarification` - Boolean flag
- `issue` - Optional description of problem
- `suggested_activity` - Auto-judge suggestion
- `suggested_classification` - Suggestion classification
- `suggestion_confidence` - Suggestion confidence (0.0-1.0)

### WeatherData

Weather information from API.

- `city, country` - Location info
- `latitude, longitude` - Coordinates
- `temperature` - Current temp
- `feels_like` - Feels-like temperature
- `humidity` - Humidity percentage
- `rain_1h` - Rainfall in past hour (mm)
- `is_raining` - Boolean flag
- `wind_speed` - Wind speed (m/s or mph)
- `wind_mph` - Wind in miles per hour
- `condition` - Weather type (Clear, Rain, etc.)
- `description` - Detailed description
- `icon_code` - Weather icon code
- `units` - "metric" or "imperial"

**Properties:**

- `temp_unit` - Returns "°C" or "°F"
- `temp_celsius` - Converts temp to Celsius
- `get_emoji()` - Returns weather emoji

### SkyScoreResult

Scoring result.

- `score` - Final score (0-100)
- `classification` - Activity type
- `weather_factors` - List of factor descriptions
- `bonuses` - List of (name, value, description) tuples
- `penalties` - List of (name, value, description) tuples
- `recommendation` - Text recommendation

### HistoryEntry

Saved analysis record.

- `timestamp` - When analysis was done
- `activity` - Activity name
- `classification` - Type
- `score` - Score result
- `city` - Location
- `weather_condition` - Weather at time

## Frontend Types (TypeScript)

### API Response Types

Located in `frontend/src/types/api.ts`

- `TaskAnalysis` - Task analysis response
- `WeatherData` - Weather data response
- `AnalysisResponse` - Complete analysis result
- `SkyScoreResult` - Scoring result
- `FactorDetail` - Weather factor detail

## Data Flow

```
User Input
    ↓
analyze_task (ai_engine.py)
    ↓
TaskAnalysis (dataclass)
    ↓
API Response (converted)
    ↓
Frontend Types
    ↓
React Components
```
