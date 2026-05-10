# Deployment Guide

SkyCoach AI ships as a **FastAPI backend on Render** and a **React/Vite SPA on Netlify**. The two are wired together by Netlify's `/api/*` redirect, so the frontend can call relative URLs and the SPA never has to know the backend's hostname.

```
   browser ──► https://your-site.netlify.app/api/predict
                       │
                       ▼  (Netlify redirect, no CORS)
              https://skycoach-api.onrender.com/api/predict
```

---

## Prerequisites

- A GitHub repo with this codebase pushed
- A Render account (free tier is fine)
- A Netlify account (free tier is fine)
- An OpenAI API key (optional - only used when the user enables it per request)
- An OpenWeather API key (optional - the demo weather path works without it)

---

## 1. Backend on Render (one click)

1. Push the repo to GitHub.
2. In Render, click **New** → **Blueprint** and pick this repo.
3. Render reads [render.yaml](render.yaml) and provisions a `skycoach-api` web service running `uvicorn backend.main:app`.
4. When prompted, paste your secrets:
   - `OPENAI_API_KEY`
   - `OPENWEATHER_API_KEY`
5. Wait for the first deploy. Hit the health endpoint to verify:
   ```
   https://skycoach-api.onrender.com/api/health
   ```

Render uses the slim [`requirements.txt`](requirements.txt) (no TensorFlow / PyTorch / Streamlit) and the Python version pinned in [`runtime.txt`](runtime.txt). The trained model itself ships as JSON inside the repo at `ml_system/models/current/`, so the server doesn't need to retrain.

### If you want a different Render service name

Edit `render.yaml` (`name: skycoach-api`) and update the `to = ...` URL in `netlify.toml` to match. Or set `RENDER_API_URL` in the Netlify dashboard and override the redirect there.

---

## 2. Frontend on Netlify (one click)

1. In Netlify, click **Add new site** → **Import an existing project** → pick the repo.
2. Netlify reads [netlify.toml](netlify.toml). The base directory is `frontend`, the build command is `npm ci && npm run build`, and the publish directory is `dist`.
3. The default deploy uses the relative `/api/*` proxy, so no env vars are required to get a working site.

### Optional environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_URL` | `""` (relative) | Set to a full URL (e.g. `https://skycoach-api.onrender.com`) to bypass the Netlify redirect and call Render directly. Leave empty to use the proxy. |
| `VITE_USE_DEMO_WEATHER` | `false` | `true` keeps the deterministic demo weather path even in production. |
| `VITE_OPENAI_MODEL` | `gpt-4o-mini` | Override the model used when the user enables OpenAI. |

---

## 3. Local development

Backend (works on Python 3.11 / 3.12; 3.14 has no wheels for some optional libs):

```powershell
cd "e:\Java\Project\Project Ai"
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8012
```

For the optional Streamlit dashboard or the optional TensorFlow / PyTorch training backends:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
```

Frontend:

```powershell
cd "e:\Java\Project\Project Ai\frontend"
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

The dev server reads `frontend/.env.local` so you can point it at any backend you want (defaults to `http://127.0.0.1:8012`).

---

## 4. ML deployment notes

- **Inference is pure Python.** The FastAPI server loads the trained model from `ml_system/models/current/model.json` at startup. No GPU, no TF, no PyTorch needed at serving time.
- **Optional accelerated training** (PyTorch / TensorFlow) is gated behind `CONFIG.linear_backend` in [`ml_system/config/settings.py`](ml_system/config/settings.py). The default `"scratch"` uses pure Python and runs anywhere.
- **Re-training in cloud** is not the default. Train locally and commit `ml_system/models/current/`, or run `python -m ml_system.training.trainer` once on a beefier dyno.
- **Model comparison endpoint:** `GET /api/model-comparison` returns the contents of `ml_system/models/current/evaluation_report.json`. Pass `?refresh=true` to recompute on demand.

---

## 5. Troubleshooting

**Render build fails with "Could not find tensorflow".**
Confirm that `requirements.txt` is the slim runtime list shipped at the repository root. TensorFlow, PyTorch, and Streamlit are intentionally omitted from the runtime requirements; they live in `requirements-dev.txt` for local use only.

**Netlify build fails with `command not found: npm ci`.**
Set `NODE_VERSION = "20"` in the Netlify UI under *Site settings → Build & deploy → Environment*. The repository's `netlify.toml` already specifies this for new sites.

**The deployed frontend reports CORS errors.**
Either `VITE_API_URL` points at a full backend URL while the Netlify domain is not listed in `ALLOWED_ORIGINS` or `ALLOWED_ORIGIN_REGEX` on the backend, or the redirect in `netlify.toml` is pointed at the wrong service. Update the environment variables, or remove `VITE_API_URL` so the proxy redirect is used.

**Local backend imports fail with `ModuleNotFoundError: streamlit`.**
The Streamlit dependencies are imported lazily inside [`services/maps.py`](services/maps.py). If the Streamlit UI is being used directly, install the development extras with `pip install -r requirements-dev.txt`.
