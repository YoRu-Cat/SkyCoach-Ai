# Frontend

React + TypeScript + Vite frontend for SkyCoach AI.

## Run

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL: http://127.0.0.1:5173/index.html

## Backend Connection

Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8012
```

## API Expectations

- Task analysis endpoints are local-model based.
- Suggestion fields are available in analysis responses.
- Chat assistant endpoint is the OpenAI-backed flow.

## Main Source Areas

- `src/components/`
- `src/pages/`
- `src/services/api.ts`
- `src/hooks/`
