# API Response Format

## `POST /api/analyze`

Top-level keys:

- `task`
- `weather`
- `score_result`
- `alternatives`

## `task` keys

- `original_text`
- `cleaned_text`
- `activity`
- `classification`
- `confidence`
- `reasoning`
- `needs_clarification`
- `issue`
- `suggested_activity`
- `suggested_classification`
- `suggestion_confidence`

## `weather` keys

- `city`
- `country`
- `latitude`
- `longitude`
- `temperature`
- `feels_like`
- `humidity`
- `rain_1h`
- `is_raining`
- `wind_speed`
- `wind_mph`
- `condition`
- `description`
- `icon_code`
- `units`
- `temp_unit`

## `score_result` keys

- `score`
- `classification`
- `weather_factors`
- `bonuses`
- `penalties`
- `recommendation`

## Notes

- Suggestion fields can be present with or without clarification.
- Task analysis is local-model based.
- Chat endpoint is separate (`/api/chat-assistant`).
