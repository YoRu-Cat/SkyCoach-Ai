# API Routes

Location: `backend/api/routes.py`

## Base

- Prefix: `/api`
- Local dev base URL: http://127.0.0.1:8012

## Core Endpoints

- `POST /api/analyze-task`
- `POST /api/weather`
- `POST /api/score`
- `POST /api/analyze`
- `POST /api/backend-cli`
- `GET /api/alternatives`
- `GET /api/health`

## ML Endpoints

- `POST /api/predict`
- `POST /api/feedback`
- `GET /api/learning-status`

## Chat Endpoint

- `POST /api/chat-assistant`

## Behavior Notes

- `POST /api/analyze-task` and `POST /api/analyze` support optional OpenAI analysis via:
  - `use_openai`
  - `openai_api_key`
  - `openai_model`
- If OpenAI is unavailable or key is missing, task analysis safely falls back to local hybrid inference.
- `POST /api/predict` returns compatibility aliases:
  - `predicted_label`
  - `predicted_confidence`
- `POST /api/analyze` response key for score is `score_result`.
- `POST /api/analyze` is resilient to forecast fetch failures and continues with current weather plus empty forecast slots.
- `POST /api/backend-cli` only accepts safe predefined commands (`help`, `health`, `version`, `time`, `weather`, `analyze`).

## Health Example

```json
{
  "status": "healthy",
  "service": "SkyCoach API",
  "version": "1.0.0"
}
```
