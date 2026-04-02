# Scoring Engine Module

**Location:** `core/scoring_engine.py`

## Purpose
Calculates SkyScore (0-100) rating for activities based on weather conditions and activity type using a decision matrix.

## Key Functions

### `calculate_sky_score(task, weather, config)`
Main scoring function that evaluates activity suitability.  
**Input:**
- TaskAnalysis: Classified activity with confidence
- WeatherData: Current weather conditions
- Config: Scoring thresholds and penalties

**Output:** SkyScoreResult with score, factors, bonuses/penalties, recommendation

### `get_alternative_activities(classification, weather)`
Suggests 3-4 alternative activities based on weather and classification.  
**Output:** List of tuples (activity_emoji_name, description)

## Scoring Decision Matrix

| Condition | Activity Type | Adjustment |
|-----------|---------------|-----------|
| Rain > 0mm | Outdoor | -80% penalty |
| Wind > 15mph | Outdoor | -30% penalty |
| Rain > 0mm | Indoor | +20% bonus |
| Temp > 30°C | Indoor | +10% bonus |

## Score Interpretation

| Score Range | Meaning | Emoji |
|------------|---------|-------|
| 80-100 | Perfect conditions | 🎉 |
| 60-79 | Good conditions | 👍 |
| 40-59 | Moderate conditions | ⚠️ |
| 20-39 | Poor conditions | 🔶 |
| 0-19 | Not recommended | ❌ |

## Configuration Parameters

```python
rain_threshold: 0.0 mm
wind_threshold_mph: 15.0 mph
heat_threshold_c: 30.0 °C
```

## Weather Factors Tracked
- 🌧️ Rainfall
- 💨 Wind speed
- 🌡️ Temperature
- ☀️ Clear conditions
- 🍃 Light wind

## Alternative Suggestions

**Outdoor Activities:**
- 🚶 Go for a walk
- 🚴 Cycling
- 🌱 Gardening
- 📸 Photography
- 🏃 Jogging
- 🎣 Fishing

**Indoor Activities:**
- 📚 Reading
- 🎮 Gaming
- 🧘 Yoga
- 👨‍🍳 Cooking
- 🎨 Art & Crafts
- 🎬 Movie marathon

**Rainy Day Specific:**
- ☕ Coffee & reading
- 🎵 Listen to music
- 📝 Journaling
- 🧩 Puzzles

**Hot Weather Specific:**
- 🏊 Swimming
- 🍦 Ice cream trip
- 🛒 Mall visit
