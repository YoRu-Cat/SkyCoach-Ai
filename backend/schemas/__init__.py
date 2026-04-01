"""Backend API schemas and request/response models."""

from .models import (
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    WeatherRequest,
    WeatherResponse,
    SkyScoreRequest,
    SkyScoreResponse,
    AlternativeActivitiesResponse,
)

__all__ = [
    "TaskAnalysisRequest",
    "TaskAnalysisResponse",
    "WeatherRequest",
    "WeatherResponse",
    "SkyScoreRequest",
    "SkyScoreResponse",
    "AlternativeActivitiesResponse",
]
