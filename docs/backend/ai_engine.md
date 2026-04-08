# AI Engine

Location: `services/ai_engine.py`

## Purpose

Provide task analysis, clarification logic, and weather utilities used by API routes.

## Active Behavior

- `analyze_task_smart(...)` is the active analyzer used by API routes.
- In current route usage, task-analysis endpoints call smart analysis with local mode.
- OpenAI-based function exists but is not the active path for task classification endpoints.

## Relevant Functions

- `analyze_task_smart(text, use_openai, openai_api_key, model)`
- `analyze_task_fallback(text)`
- `analyze_task_openai(text, api_key, model)` (available, not primary in active task endpoints)
- `get_weather(...)`
- `get_demo_weather(...)`
- `get_weather_by_city(...)`

## Output Characteristics

Task analysis output includes:

- `activity`
- `classification`
- `confidence`
- `reasoning`
- `needs_clarification`
- `issue`
- `suggested_activity`
- `suggested_classification`
- `suggestion_confidence`

## Runtime Notes

- Confidence threshold in `ml_system` config: 0.62
- Suggestion fields are used for autocorrect-like UX when input is ambiguous
