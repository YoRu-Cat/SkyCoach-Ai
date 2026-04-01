# Full Stack Setup & Development Guide

## Quick Start (Both Frontend & Backend)

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to project root:

```bash
cd "e:\Java\Project\Project Ai"
```

2. Ensure Python dependencies are installed:

```bash
pip install -r requirements.txt
```

3. Start FastAPI backend:

```bash
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: `http://localhost:8000`

API docs available at: `http://localhost:8000/docs`

### Frontend Setup

In a new terminal:

1. Navigate to frontend:

```bash
cd "e:\Java\Project\Project Ai\frontend"
```

2. Install dependencies:

```bash
npm install
```

3. Start development server:

```bash
npm run dev
```

Frontend will open at: `http://localhost:3000`

## Full Stack Components

### Backend (FastAPI)

```
Location: e:\Java\Project\Project Ai\
Endpoints:
  - POST /api/analyze-task      Task analysis
  - POST /api/weather           Weather data
  - POST /api/score             SkyScore calculation
  - POST /api/analyze           Full pipeline
  - GET /api/alternatives       Alternative suggestions
  - GET /api/health             Health check
  - GET /docs                   Swagger UI
```

### Frontend (React)

```
Location: e:\Java\Project\Project Ai\frontend
Port: 3000
Components:
  - Dashboard (main page)
  - ActivityInput (form)
  - TaskCard (analysis)
  - WeatherCard (weather)
  - ScoreCard (scoring)
  - AlternativesCard (suggestions)
  - Header (navigation)
```

### Streamlit App (Legacy)

```
Location: e:\Java\Project\Project Ai\app.py
Port: 8501
Command: python -m streamlit run app.py
```

## Development Workflow

### 1. Terminal 1 - Backend

```bash
cd "e:\Java\Project\Project Ai"
python -m uvicorn backend.main:app --reload
```

Keep running during development.

### 2. Terminal 2 - Frontend

```bash
cd "e:\Java\Project\Project Ai\frontend"
npm run dev
```

Keep running during development.

### 3. Browser

Open `http://localhost:3000` and start developing.

Both have hot reload enabled.

## Testing Individual Endpoints

### Using curl (Windows with curl installed)

```bash
# Task analysis
curl -X POST http://localhost:8000/api/analyze-task ^
  -H "Content-Type: application/json" ^
  -d "{\"text\":\"playing soccer\",\"use_openai\":false}"

# Full analysis
curl -X POST http://localhost:8000/api/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"activity_text\":\"doing homework\",\"city\":\"New York\",\"use_openai\":false,\"use_demo_weather\":true}"
```

### Using Swagger UI

```
http://localhost:8000/docs
```

Interactive API documentation. Click "Try it out" on any endpoint.

## Project Structure Overview

```
Project Ai/
├── app.py                       # Streamlit UI (legacy)
├── requirements.txt             # Python dependencies
├── backend/                     # FastAPI server
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   └── schemas/
│       └── models.py
├── frontend/                    # React app (NEW)
│   ├── package.json
│   ├── index.html
│   ├── index.tsx
│   ├── vite.config.ts
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── hooks/
├── services/                    # Python services
│   ├── ai_engine.py
│   ├── auto_judge.py
│   └── maps.py
├── core/                        # Business logic
│   ├── pipeline.py
│   └── scoring_engine.py
└── models/                      # Data structures
    └── data_classes.py
```

## Troubleshooting

### Backend Connection Error in React

**Symptom**: "Could not connect to SkyCoach API"

**Solution**:

1. Verify backend is running: `http://localhost:8000/api/health`
2. Check CORS configuration in `backend/main.py`
3. Update `frontend/.env` with correct `VITE_API_URL`

### Port Already in Use

**Backend**:

```bash
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use different port
python -m uvicorn backend.main:app --port 8001
```

**Frontend**:
Edit `frontend/vite.config.ts`:

```typescript
server: {
  port: 3001,  // Change to 3001
}
```

### Dependencies Issues

**Python**:

```bash
pip install --upgrade -r requirements.txt
```

**Node**:

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Building for Production

### Backend

```bash
# No build needed, just run with production settings
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm run build
npm run preview  # Test production build locally
```

Output in `frontend/dist/`

## Environment Configuration

### Backend

Set Python environment variables:

```bash
set OPENAI_API_KEY=your_key_here
set OPENWEATHER_API_KEY=your_key_here
```

### Frontend

Edit `frontend/.env`:

```env
VITE_API_URL=http://localhost:8000
VITE_APP_NAME=SkyCoach AI
```

## Performance Tips

### Backend

- Use demo weather to avoid rate limits
- Cache API responses (React Query handles this)
- Monitor with `uvicorn` logs

### Frontend

- Inspect network with browser DevTools
- Check "Network" tab for API response times
- Profile components with React DevTools

## Monitoring

### Backend Health

```bash
curl http://localhost:8000/api/health
```

Response:

```json
{
  "status": "healthy",
  "service": "SkyCoach API",
  "version": "1.0.0"
}
```

### Frontend Status

Check browser console for errors:

- `Ctrl+Shift+J` (Windows/Linux)
- `Cmd+Option+J` (Mac)

## Next Steps

1. **Frontend Styling**: Implement GSAP animations
2. **Component Details**: Add more interactive features
3. **Error Handling**: Add error boundaries
4. **Testing**: Unit tests with Vitest
5. **Deployment**: Deploy to cloud (AWS, Vercel, etc.)

## Useful Commands

```bash
# Python linting
python -m pylint services/ai_engine.py

# TypeScript type check
cd frontend && npx tsc --noEmit

# Format code
cd frontend && npm run format

# Build frontend
cd frontend && npm run build

# Check tree of files
tree /F "e:\Java\Project\Project Ai\frontend\src"
```

## API Documentation

Once both are running:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Frontend**: http://localhost:3000

## Support & Logs

### Backend Logs

Check terminal where `uvicorn` is running:

```
INFO:     Application startup complete.
GET /api/health 200 OK
POST /api/analyze-task 200 OK
```

### Frontend Logs

Check browser console (F12):

```
[React DevTools] React is running in development mode
API connected at http://localhost:8000
```

---

**Session Status**: Multi-terminal full-stack development environment ready!
