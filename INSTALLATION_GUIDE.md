# Installation & Setup Guide

## Prerequisites Check

### Node.js & npm

Node.js is **not currently installed** on this system. You'll need to install it to run the React frontend.

**Download & Install:**

1. Go to https://nodejs.org/
2. Download the **LTS version** (18.x or newer)
3. Run the installer
4. During installation, ensure both Node.js and npm are checked
5. Accept default settings
6. Restart your terminal/PowerShell

**Verify Installation:**

After restart, run:

```bash
node --version
npm --version
```

Should output version numbers like:

```
v18.16.0
9.8.0
```

### Python Dependencies

Python dependencies in `requirements.txt` are **installed**. Backend API is ready:

```bash
python -m uvicorn backend.main:app --reload
```

## Backend Setup (Python - Ready Now)

The FastAPI backend is ready to run immediately:

```bash
cd "e:\Java\Project\Project Ai"
python -m uvicorn backend.main:app --reload
```

Available at: http://localhost:8000

### Verify Backend

```bash
curl http://localhost:8000/api/health
```

Or open: http://localhost:8000/docs

## Frontend Setup (Node.js - After Installation)

Once Node.js is installed:

```bash
cd "e:\Java\Project\Project Ai\frontend"
npm install
npm run dev
```

Available at: http://localhost:3000

## Complete Installation Order

1. **Install Node.js + npm** from nodejs.org
2. **Start Backend**:
   ```bash
   cd "e:\Java\Project\Project Ai"
   python -m uvicorn backend.main:app --reload
   ```
3. **Install Frontend** (in new terminal):
   ```bash
   cd "e:\Java\Project\Project Ai\frontend"
   npm install
   npm run dev
   ```
4. **Open Browser**: http://localhost:3000

## Troubleshooting

### Node.js not found after installation

- Close and reopen PowerShell/Terminal
- Try in Command Prompt (cmd.exe) instead
- Check System Environment Variables (Path)

### npm install is slow

- Use `npm install --legacy-peer-deps` if dependency conflicts occur
- Check internet connection
- Try `npm cache clean --force`

### Port 3000 already in use

Edit `frontend/vite.config.ts`:

```typescript
server: {
  port: 3001,  // Change to 3001
}
```

### Port 8000 already in use

```bash
python -m uvicorn backend.main:app --port 8001
```

## What's Already Set Up

✓ **Backend (FastAPI)**

- Python dependencies installed
- API routes configured
- Auto-judge feature working
- Health checks ready

✓ **Frontend (React - Pending npm)**

- All source files created
- TypeScript configured
- TailwindCSS configured
- Vite config ready
- Components written
- Just needs: `npm install`

## Development Environment

After Node.js installation and `npm install`:

```bash
# Terminal 1: Backend
python -m uvicorn backend.main:app --reload

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3 (Optional): Legacy Streamlit
python -m streamlit run app.py
```

## System Check Script

After Node.js installation, run this to verify everything:

```bash
echo "=== Python ==="
python --version

echo "=== Node.js ==="
node --version && npm --version

echo "=== Backend ==="
echo "Checking if uvicorn installed..."
python -m pip list | findstr fastapi

echo "=== Frontend ==="
echo "Checking if node_modules exist..."
Test-Path "e:\Java\Project\Project Ai\frontend\node_modules"
```

## Next Steps

1. **Install Node.js** → https://nodejs.org/
2. **Restart Terminal/PowerShell**
3. **Run**: `npm install` in frontend directory
4. **Start dev servers** (see above)
5. **Open**: http://localhost:3000

---

**Status**: Backend ready, Frontend waiting for Node.js
