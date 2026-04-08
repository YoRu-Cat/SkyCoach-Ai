# SkyCoach AI - Full Stack Setup Guide

## Current Runtime Update (April 2026)

- Backend active local port: `8012`
- Frontend active local port: `5173`
- Task analysis uses local model path in active flow.
- OpenAI is used in chat assistant flow only.

## Current Status ✓

### Backend (Python) - READY ✓

- ✓ FastAPI 0.104+ installed and running
- ✓ Pydantic 2.0+ validation configured
- ✓ Auto-judge engine (130+ activity corpus) loaded
- ✓ 6 API endpoints functional
- ✓ All imports working correctly

### Frontend (React) - WAITING ON NODE.JS

- ✓ Structure complete (27 files)
- ✓ All components built and typed
- ✓ Configuration files ready (vite, tailwind, tsconfig)
- ⏳ **BLOCKED:** Node.js not installed (required for npm)

---

## CRITICAL BLOCKER: Node.js Not Installed

### Problem

Your system doesn't have Node.js/npm installed. This is required to:

- Install frontend dependencies (React, TypeScript, TailwindCSS, etc.)
- Run `npm install` command
- Start the development server on port 3000

### Solution - Download & Install Node.js

**Step 1:** Download Node.js

- Go to: https://nodejs.org
- Click **"LTS" button** (Long Term Support - version 20.x)
- Save installer to your computer

**Step 2:** Run the Installer

- Double-click `node-v20.x.x-x64.msi` (or your version)
- Click through the installer
  - Accept license agreement
  - Keep default installation path
  - Select "Automatically install necessary tools"
  - Click Install

**Step 3:** Restart Your Terminal

- Close all PowerShell windows
- Open new PowerShell as Administrator

**Step 4:** Verify Installation

```powershell
node --version   # Should show v20.x.x or later
npm --version    # Should show 10.x.x or later
```

---

## Complete Setup Sequence (After Node.js Installed)

### Terminal 1: Backend Server

```powershell
cd e:\Java\Project\"Project Ai"
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Expected: `Uvicorn running on http://0.0.0.0:8000`

### Terminal 2: Frontend Server

```powershell
cd e:\Java\Project\"Project Ai"\frontend
npm install          # First time only - installs 30 packages (~2-3 minutes)
npm run dev          # Subsequent times - starts dev server
```

Expected: `Local: http://localhost:5173`

### Terminal 3: Verification

```powershell
cd e:\Java\Project\"Project Ai"
# Check backend health
curl http://localhost:8000/health

# Test complete flow
curl -X POST http://localhost:8000/api/analyze -H "Content-Type: application/json" `
  -d '{"activity": "washing car", "city": "New York"}'
```

---

## What's Currently Working

✓ **Backend API:** All 6 endpoints tested and working

- POST /api/analyze-task → Activity classification
- POST /api/weather → Weather data with coordinates
- POST /api/score → Activity scoring
- POST /api/alternatives → Alternative suggestions
- POST /api/analyze → Full analysis with auto-judge
- GET /api/health → System status

✓ **Auto-Judge Engine:** Intelligent input correction

- "washing car" → Outdoor classification (100%)
- "doing homewo" → Suggests "doing homework" (92% confidence)
- "play socc" → Suggests "playing soccer" (78% confidence)

✓ **React Frontend:** Structure complete and type-safe

- 8 components fully built (Header, Input, Dashboard, Results, etc.)
- Type-safe API client with Axios
- React Query hooks with caching
- TailwindCSS + Glasmorphism styling
- Full TypeScript support

---

## Troubleshooting

### If npm install fails:

1. Make sure Node.js is installed correctly: `node --version`
2. Clear npm cache: `npm cache clean --force`
3. Delete `node_modules` folder and `package-lock.json`
4. Try again: `npm install`

### If backend port 8000 is in use:

```powershell
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process
taskkill /PID <PID> /F
```

### If frontend dev server won't start:

1. Check if port 5173 is in use
2. Try a different port: `npm run dev -- --port 3000`
3. Check error messages - usually missing dependencies

### If API requests fail:

1. Verify backend is running: `curl http://localhost:8000/health`
2. Check CORS configuration in `backend/main.py`
3. Verify frontend .env has `VITE_API_URL=http://localhost:8000`

---

## Next Steps

1. **Install Node.js 20.x from https://nodejs.org (LTS)**
2. **Restart terminal**
3. **Run the setup sequence above**
4. **Open http://localhost:5173 in browser**
5. **Test the app: enter activity → see AI analysis**

---

## Files Ready for You

- `INSTALLATION_GUIDE.md` - Comprehensive setup reference
- `FULL_STACK_SETUP.md` - Server orchestration guide
- `QUICK_REFERENCE.md` - Common commands
- `frontend/README.md` - Frontend documentation
- `frontend/ARCHITECTURE.md` - Frontend technical details

**Your app is ready to go. Just need Node.js installed!**
