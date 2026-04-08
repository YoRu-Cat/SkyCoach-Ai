# Full Stack Setup

## Current Runtime

- Backend: 127.0.0.1:8012
- Frontend: 127.0.0.1:5173
- Task analysis: local model path
- OpenAI: chat assistant only

## Prerequisites

- Python 3.10+
- Node.js 18+

## Install

```powershell
cd "e:\Java\Project\Project Ai"
pip install -r requirements.txt
```

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
```

## Run Backend

```powershell
cd "e:\Java\Project\Project Ai"
E:/Anaconda/Installed/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

## Run Frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## Verify

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/health
Invoke-WebRequest -Uri http://127.0.0.1:5173/index.html
```

## URLs

- App: http://127.0.0.1:5173/index.html
- API docs: http://127.0.0.1:8012/docs
