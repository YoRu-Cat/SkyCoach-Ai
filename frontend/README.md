# Frontend

React + TypeScript + Vite frontend for SkyCoach AI.

## Run

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
npm.cmd run dev -- --host 127.0.0.1 --port 5173
```

Frontend URL: <http://127.0.0.1:5173/index.html>

## Backend Connection

Create `frontend/.env.local`:

```env
VITE_API_URL=http://127.0.0.1:8012
```

## API Expectations

- Task analysis endpoints are hybrid smart-analysis based (local default, OpenAI optional when enabled).
- Suggestion fields are available in analysis responses.
- Chat assistant endpoint is the OpenAI-backed flow.

## Current UX Modules

- Dashboard/Home: quick status, chat assistant, backend terminal view.
- Todo: editable event and notes fields, reminders, due-task activity check.
- Timetable: 1-week schedule controls with conflict-safe slot updates.
- Weather Planner: weather-aware recommendation pipeline using the same full-analysis model path as Core.

## Reminder Behavior

- Uses browser Notification API permission model.
- Plays ringtone presets (bell/chime/alarm) and attempts vibration.
- Shows due-task prompt with two actions:
  - Yes, completed
  - No, reschedule to next available slot

## Main Source Areas

- `src/components/`
- `src/pages/`
- `src/services/api.ts`
- `src/hooks/`
