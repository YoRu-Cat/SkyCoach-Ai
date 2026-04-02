import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router

app = FastAPI(
    title="SkyCoach API",
    description="Weather-based activity scoring API",
    version="1.0.0",
)

def _parse_origins(env_value: str) -> list[str]:
    return [origin.strip() for origin in env_value.split(",") if origin.strip()]


default_dev_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://localhost:8501",
    "http://localhost:8000",
    "http://localhost:8512",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8512",
]

origins_env = os.getenv("ALLOWED_ORIGINS", "")
origins = _parse_origins(origins_env) if origins_env else default_dev_origins

# Optional: set this for Netlify preview URLs, e.g. r"https://.*--your-site\.netlify\.app"
origin_regex = os.getenv("ALLOWED_ORIGIN_REGEX")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to SkyCoach API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
