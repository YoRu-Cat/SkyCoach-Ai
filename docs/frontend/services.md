# Frontend Services

Location: `frontend/src/services/`

## API Base URL

Frontend API calls should target the backend configured by `VITE_API_URL`.

Recommended local value:

```env
VITE_API_URL=http://127.0.0.1:8012
```

## Service Responsibilities

- Send task-analysis requests
- Send full-analysis requests
- Fetch weather and alternatives
- Handle learning endpoints (predict/feedback/status)
- Handle chat assistant calls

## Runtime Notes

- Task analysis is local-model driven in backend routes.
- OpenAI is used in chat assistant flow.
