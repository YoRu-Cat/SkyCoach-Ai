# Installation Guide

## Prerequisites

- Python 3.10+
- Node.js 18+

## Install Dependencies

```powershell
cd "e:\Java\Project\Project Ai"
pip install -r requirements.txt
```

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
```

## Frontend Environment

Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8012
```

## Run Services

### Backend

```powershell
cd "e:\Java\Project\Project Ai"
E:/Anaconda/Installed/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

### Frontend

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

## Verify

```powershell
Invoke-WebRequest -Uri http://127.0.0.1:8012/api/health
Invoke-WebRequest -Uri http://127.0.0.1:5173/index.html
```

## Notes

- Task analysis is local-model based in active flow.
- OpenAI is used for chat assistant flow only.
- Current inference confidence threshold is 0.62.
