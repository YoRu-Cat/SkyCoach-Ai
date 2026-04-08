# Backend API

## Base URL

- Local dev: http://127.0.0.1:8012
- API docs: http://127.0.0.1:8012/docs

## Architecture Notes

- Task analysis endpoints run local analysis path.
- OpenAI is used only by chat assistant flow.
- Inference confidence threshold is 0.62.

## Endpoints

### Health

- `GET /api/health`

### Analysis

- `POST /api/analyze-task`
- `POST /api/analyze`

### Weather and Scoring

- `POST /api/weather`
- `POST /api/score`
- `GET /api/alternatives`

### Learning

- `POST /api/predict`
- `POST /api/feedback`
- `GET /api/learning-status`

### Chat

- `POST /api/chat-assistant`

## Example Analyze Request

```json
{
  "activity_text": "going to get cigarettes from tobacco shop",
  "city": "New York",
  "use_openai": false,
  "use_demo_weather": true
}
```

## Example Analyze Response Shape

```json
{
  "task": {},
  "weather": {},
  "score_result": {},
  "alternatives": []
}
```
