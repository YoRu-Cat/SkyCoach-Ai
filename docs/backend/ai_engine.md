# AI Engine Module

**Location:** `services/ai_engine.py`

## Current Runtime Update (April 2026)

- Active task analysis flow is local and context-aware.
- OpenAI is no longer used in task-analysis endpoints; only chat assistant uses OpenAI.
- Current model confidence threshold is `0.62`.
- Suggestion outputs include `suggested_activity`, `suggested_classification`, and `suggestion_confidence` where relevant.

## Purpose

Analyzes activity tasks and classifies them as Indoor or Outdoor using keyword matching, optional OpenAI integration, and auto-judgment for incomplete inputs.

## Key Functions

### `analyze_task_openai(text, api_key, model)`

Uses OpenAI's GPT model to analyze and classify activities.  
**Input:** Activity description text, OpenAI API key  
**Output:** TaskAnalysis dataclass with activity, classification, confidence score

### `analyze_task_fallback(text)`

Keyword-based fallback when OpenAI is unavailable or disabled.  
Uses predefined lists of outdoor and indoor keywords to classify activity.  
**Output:** TaskAnalysis dataclass

### `get_weather(lat, lon, api_key, units)`

Fetches real weather data from OpenWeatherMap API.  
**Input:** Latitude, longitude, API key, units (metric/imperial)  
**Output:** WeatherData dataclass

### Helper Functions

- `_count_keyword_matches()` - Counts whole-word phrase matches
- `_detect_input_issue()` - Identifies incomplete or ambiguous inputs
- `_stable_fallback_coords()` - Generates deterministic coordinates for demo mode
- `_resolve_demo_city_coords()` - Resolves city names to coordinates
- `_apply_auto_judge_resolution()` - Promotes high-confidence suggestions to confirmed activities

## Keyword Lists

- **Outdoor:** soccer, football, hiking, cycling, swimming, gardening, jogging, etc.
- **Indoor:** cooking, reading, gaming, working, studying, homework, yoga, etc.

## Confidence Thresholds

- Auto-judge promotion threshold: 0.72 (72%)
- Minimum confidence to avoid "needs clarification": 0.25 (25%)

## Features

- Multi-step detection: keyword matching → OpenAI (if available) → auto-judge
- Graceful fallback to keyword-based analysis
- Handles incomplete/misspelled activity descriptions
- Built-in activity suggestion for common typos
