# SkyCoach Quick Reference

## Start Backend

```powershell
cd "e:\Java\Project\Project Ai"
E:/Anaconda/Installed/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

## Start Frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## Health Checks

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/health
Invoke-WebRequest -Uri http://127.0.0.1:5173/index.html
```

## Core Endpoints

- `POST /api/analyze-task`
- `POST /api/analyze`
- `POST /api/predict`
- `POST /api/feedback`
- `GET /api/learning-status`
- `POST /api/chat-assistant`

## Runtime Rules

- Task analysis is local-model based.
- OpenAI is chat-assistant-only.
- Confidence threshold is 0.62.
