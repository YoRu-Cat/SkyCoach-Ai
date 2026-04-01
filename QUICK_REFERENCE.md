# SkyCoach AI - Developer Quick Reference

## Project Overview

**Full-stack weather-based activity advisor** with:

- FastAPI backend (Python) on port 8000
- React frontend on port 3000
- PostgreSQL-ready architecture
- Auto-correction for incomplete inputs
- Real-time weather integration

## Quick Commands

### Start Everything

```bash
# Terminal 1: Backend
cd "e:\Java\Project\Project Ai"
python -m uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd "e:\Java\Project\Project Ai\frontend"
npm run dev

# Terminal 3 (Optional): Streamlit (legacy)
cd "e:\Java\Project\Project Ai"
python -m streamlit run app.py
```

### Build & Deploy

```bash
# Frontend production build
cd frontend
npm run build
npm run preview

# Backend is ready to deploy as-is
```

## File Locations

| Component    | Location                 | Port |
| ------------ | ------------------------ | ---- |
| Backend API  | `backend/main.py`        | 8000 |
| Frontend App | `frontend/`              | 3000 |
| Streamlit UI | `app.py`                 | 8501 |
| Services     | `services/`              | -    |
| Types        | `models/data_classes.py` | -    |

## API Endpoints

| Method | Endpoint            | Purpose            |
| ------ | ------------------- | ------------------ |
| POST   | `/api/analyze-task` | Analyze activity   |
| POST   | `/api/weather`      | Get weather        |
| POST   | `/api/analyze`      | Full pipeline      |
| GET    | `/api/alternatives` | Suggest activities |
| GET    | `/api/health`       | Health check       |
| GET    | `/docs`             | Swagger docs       |

## Key Files to Edit

### Add Feature to Backend

1. Update `services/ai_engine.py` or `core/scoring_engine.py`
2. Update `backend/api/routes.py` to expose it
3. Add TypeScript types in `frontend/src/types/api.ts`
4. Use in React with hook from `frontend/src/hooks/useApi.ts`

### Add Component to Frontend

1. Create `frontend/src/components/NewComponent.tsx`
2. Add to `frontend/src/components/index.ts`
3. Use in any page with `import { NewComponent } from '@components'`

### Update API Types

1. Edit `frontend/src/types/api.ts` with new interfaces
2. Update `frontend/src/services/api.ts` with endpoint call
3. Add hook in `frontend/src/hooks/useApi.ts`

## Technology Stack

| Layer    | Technologies                                       |
| -------- | -------------------------------------------------- |
| Backend  | Python, FastAPI, Pydantic, OpenAI                  |
| Frontend | React 18, TypeScript, Vite, TailwindCSS            |
| State    | React Query (server state), React hooks (UI state) |
| Styling  | TailwindCSS + custom CSS                           |
| HTTP     | Axios (frontend), requests (backend)               |

## Common Tasks

### Add New Activity to Auto-Judge Corpus

File: `services/auto_judge.py`

```python
ACTIVITY_CORPUS = {
    "Outdoor": [
        "your new activity",  # Add here
    ],
    "Indoor": [
        # or here
    ]
}
```

### Change API Response Type

1. Update schema: `backend/schemas/models.py`
2. Update type: `frontend/src/types/api.ts`
3. Update frontendcomponent to use new fields

### Deploy Frontend to Web

```bash
cd frontend
npm run build
# Upload dist/ to web server or Vercel/Netlify
```

## Debugging

### Backend Debug

```python
# Add logging in services
import logging
logging.debug(f"Variable: {var}")

# Run with debug logs
python -m uvicorn backend.main:app --log-level debug
```

### Frontend Debug

```typescript
// Browser DevTools
console.log("State:", data);
debugger; // Pause execution

// React DevTools browser extension
// Check component props and state
```

### Check API Response

```bash
# Terminal
curl -X POST http://localhost:8000/api/analyze-task \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"test\",\"use_openai\":false}"

# Or use Swagger: http://localhost:8000/docs
```

## Environment Variables

### Backend (Python)

```bash
OPENAI_API_KEY=sk-...
OPENWEATHER_API_KEY=...
```

### Frontend (Node)

```env
# frontend/.env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SkyCoach AI
```

## Testing

### Manual Testing

1. Open http://localhost:3000
2. Enter activity: "doing homewo"
3. See auto-correction suggestion: "doing homework"
4. View weather and SkyScore

### Test Incomplete Input

```
Input: "play socc"
Expected: Auto-suggestion for "playing soccer"
```

### Test Weather

```
City: "New York" or any city
Expected: Temperature, condition, wind, humidity
```

## Performance

- Backend: <100ms per request (demo mode)
- Frontend: <500ms load time
- React Query caches results automatically
- Vite dev server has instant HMR

## Monitoring

### Health Checks

```bash
curl http://localhost:8000/api/health
curl http://localhost:3000  (browser loads)
```

### Logs

```
Backend: Check terminal running uvicorn
Frontend: Press F12 → Console tab
```

## Security Notes

- No hardcoded API keys (use .env)
- CORS configured for localhost
- Update before production deployment
- API authentication ready to implement

## Directory Tree

```
Project Ai/
├── backend/api/routes.py
├── services/{ai_engine, auto_judge, maps}.py
├── frontend/src/{components, pages, services, hooks}/
├── app.py (Streamlit legacy UI)
└── models/, core/, components/
```

## Useful Links

- Swagger API Docs: http://localhost:8000/docs
- React DevTools: Browser extension
- Vite Docs: https://vitejs.dev
- TailwindCSS Docs: https://tailwindcss.com
- FastAPI Docs: https://fastapi.tiangolo.com

## Shortcut Commands

```bash
# Install all Python deps
pip install -r requirements.txt

# Install all Node deps
cd frontend && npm install

# Format code
cd frontend && npm run format
cd .. && black services/

# Type check
cd frontend && npx tsc --noEmit

# Build frontend
cd frontend && npm run build

# Preview build
cd frontend && npm run preview
```

## When Something Breaks

1. **Backend won't start**: Check port 8000 is free
2. **Frontend won't load**: Check backend on :8000/api/health
3. **API call fails**: Check requests in browser Network tab
4. **Types mismatch**: Update frontend/src/types/api.ts
5. **Component error**: Check browser console (F12)

## Next Development Tasks

- [ ] Task #9: Dynamic weather backgrounds
- [ ] Task #14: Migrate remaining UI components
- [ ] Task #15: Add GSAP animations
- [ ] Task #16: Deploy to production

---

**Last Updated**: 2026-04-02
**Status**: Full-stack development environment ready
