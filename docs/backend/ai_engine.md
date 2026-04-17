# AI Engine

Location: `services/ai_engine.py`

## Purpose

Provide task analysis, clarification logic, and weather utilities used by API routes.

## Active Behavior

- `analyze_task_smart(...)` is the active analyzer used by API routes.
- Smart analyzer chooses OpenAI path only when explicitly requested and key is available.
- Otherwise it uses local fallback (ML + dictionary + token semantics).
- If OpenAI errors, it automatically degrades to local fallback with reasoning annotation.

## Relevant Functions

- `analyze_task_smart(text, use_openai, openai_api_key, model)`
- `analyze_task_fallback(text)`
- `analyze_task_openai(text, api_key, model)`
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
- Fallback reasoning explicitly indicates cross-validation path when OpenAI is unavailable
