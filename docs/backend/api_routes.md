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
- `GET /api/alternatives`
- `GET /api/health`

## ML Endpoints

- `POST /api/predict`
- `POST /api/feedback`
- `GET /api/learning-status`

## Chat Endpoint

- `POST /api/chat-assistant`

## Behavior Notes

- `POST /api/analyze-task` and `POST /api/analyze` use local task-analysis path in active flow.
- `POST /api/predict` returns compatibility aliases:
  - `predicted_label`
  - `predicted_confidence`
- `POST /api/analyze` response key for score is `score_result`.

## Health Example

```json
{
  "status": "healthy",
  "service": "SkyCoach API",
  "version": "1.0.0"
}
```
