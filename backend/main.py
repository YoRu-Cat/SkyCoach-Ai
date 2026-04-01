"""FastAPI application initialization and configuration."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import router

app = FastAPI(
    title="SkyCoach API",
    description="Weather-based activity scoring API",
    version="1.0.0",
)

origins = [
    "http://localhost:3000",
    "http://localhost:8501",
    "http://localhost:8000",
    "http://localhost:8512",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8501",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8512",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
async def root():
    """Root endpoint with API documentation link."""
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
