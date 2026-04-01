"""API endpoints for task analysis and weather scoring."""

from fastapi import APIRouter, HTTPException
from typing import List, Tuple
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.ai_engine import (
    analyze_task_openai,
    analyze_task_fallback,
    get_demo_weather,
    get_weather_by_city,
)
from services.maps import render_map
from core.scoring_engine import calculate_sky_score, get_alternative_activities
from models.data_classes import Config, TaskAnalysis, WeatherData
from backend.schemas.models import (
    TaskAnalysisRequest,
    TaskAnalysisResponse,
    WeatherRequest,
    WeatherResponse,
    SkyScoreRequest,
    SkyScoreResponse,
    AlternativeActivitiesResponse,
    FactorDetail,
    AnalysisRequest,
    AnalysisResponse,
)

router = APIRouter(prefix="/api", tags=["analysis"])


def convert_task_to_response(task: TaskAnalysis) -> TaskAnalysisResponse:
    """Convert TaskAnalysis model to API response."""
    return TaskAnalysisResponse(
        original_text=task.original_text,
        cleaned_text=task.cleaned_text,
        activity=task.activity,
        classification=task.classification,
        confidence=task.confidence,
        reasoning=task.reasoning,
        needs_clarification=getattr(task, "needs_clarification", False),
        issue=getattr(task, "issue", None),
        suggested_activity=getattr(task, "suggested_activity", None),
        suggested_classification=getattr(task, "suggested_classification", None),
        suggestion_confidence=getattr(task, "suggestion_confidence", 0.0),
    )


def convert_weather_to_response(weather: WeatherData) -> WeatherResponse:
    """Convert WeatherData model to API response."""
    return WeatherResponse(
        city=weather.city,
        country=weather.country,
        latitude=weather.latitude,
        longitude=weather.longitude,
        temperature=weather.temperature,
        feels_like=weather.feels_like,
        humidity=weather.humidity,
        rain_1h=weather.rain_1h,
        is_raining=weather.is_raining,
        wind_speed=weather.wind_speed,
        wind_mph=weather.wind_mph,
        condition=weather.condition,
        description=weather.description,
        icon_code=weather.icon_code,
        units=weather.units,
        temp_unit=weather.temp_unit,
    )


@router.post("/analyze-task", response_model=TaskAnalysisResponse)
async def analyze_task(request: TaskAnalysisRequest) -> TaskAnalysisResponse:
    """Analyze an activity task and classify it."""
    try:
        if request.use_openai and request.openai_api_key:
            task = analyze_task_openai(request.text, request.openai_api_key)
        else:
            task = analyze_task_fallback(request.text)
        
        return convert_task_to_response(task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Task analysis failed: {str(e)}")


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    """Get weather data by city or coordinates."""
    try:
        if request.use_demo or not request.api_key:
            if request.city:
                weather = get_demo_weather(request.city)
            else:
                weather = get_demo_weather("New York")
        else:
            if request.city:
                weather = get_weather_by_city(request.city, request.api_key)
            elif request.latitude is not None and request.longitude is not None:
                from services.ai_engine import get_weather
                weather = get_weather(request.latitude, request.longitude, request.api_key)
            else:
                raise ValueError("Provide either city name or coordinates")
        
        return convert_weather_to_response(weather)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Weather fetch failed: {str(e)}")


@router.post("/score", response_model=SkyScoreResponse)
async def calculate_score(request: SkyScoreRequest) -> SkyScoreResponse:
    """Calculate SkyScore based on task and weather."""
    try:
        config = Config(
            rain_threshold=request.rain_threshold,
            wind_threshold_mph=request.wind_threshold_mph,
            heat_threshold_c=request.heat_threshold_c,
        )
        
        task = TaskAnalysis(
            original_text=request.task.original_text,
            cleaned_text=request.task.cleaned_text,
            activity=request.task.activity,
            classification=request.task.classification,
            confidence=request.task.confidence,
            reasoning=request.task.reasoning,
            needs_clarification=request.task.needs_clarification,
        )
        
        weather = WeatherData(
            city=request.weather.city,
            country=request.weather.country,
            latitude=request.weather.latitude,
            longitude=request.weather.longitude,
            temperature=request.weather.temperature,
            feels_like=request.weather.feels_like,
            humidity=request.weather.humidity,
            rain_1h=request.weather.rain_1h,
            is_raining=request.weather.is_raining,
            wind_speed=request.weather.wind_speed,
            wind_mph=request.weather.wind_mph,
            condition=request.weather.condition,
            description=request.weather.description,
            icon_code=request.weather.icon_code,
            units=request.weather.units,
        )
        
        result = calculate_sky_score(task, weather, config)
        
        bonuses = [
            FactorDetail(name=name, value=value, description=desc)
            for name, value, desc in result.bonuses
        ]
        penalties = [
            FactorDetail(name=name, value=value, description=desc)
            for name, value, desc in result.penalties
        ]
        
        return SkyScoreResponse(
            score=result.score,
            classification=result.classification,
            weather_factors=result.weather_factors,
            bonuses=bonuses,
            penalties=penalties,
            recommendation=result.recommendation,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Score calculation failed: {str(e)}")


@router.post("/alternatives", response_model=AlternativeActivitiesResponse)
async def get_alternatives(
    classification: str,
    weather_city: str = "New York",
    use_demo: bool = True,
) -> AlternativeActivitiesResponse:
    """Get alternative activity suggestions."""
    try:
        if use_demo:
            weather = get_demo_weather(weather_city)
        else:
            weather = get_demo_weather(weather_city)
        
        suggestions = get_alternative_activities(classification, weather)
        
        return AlternativeActivitiesResponse(
            suggestions=suggestions,
            reason=f"Based on {classification.lower()} activity and weather conditions",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not get alternatives: {str(e)}")


@router.post("/analyze", response_model=AnalysisResponse)
async def full_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Complete end-to-end analysis: task → weather → score → alternatives."""
    try:
        task = analyze_task_openai(request.activity_text, request.openai_api_key) if (request.use_openai and request.openai_api_key) else analyze_task_fallback(request.activity_text)
        
        if request.use_demo_weather or not request.weather_api_key:
            weather = get_demo_weather(request.city)
        else:
            weather = get_weather_by_city(request.city, request.weather_api_key)
        
        config = Config()
        score_result = calculate_sky_score(task, weather, config)
        alternatives = get_alternative_activities(task.classification, weather)
        
        return AnalysisResponse(
            task=convert_task_to_response(task),
            weather=convert_weather_to_response(weather),
            score_result=SkyScoreResponse(
                score=score_result.score,
                classification=score_result.classification,
                weather_factors=score_result.weather_factors,
                bonuses=[FactorDetail(name=n, value=v, description=d) for n, v, d in score_result.bonuses],
                penalties=[FactorDetail(name=n, value=v, description=d) for n, v, d in score_result.penalties],
                recommendation=score_result.recommendation,
            ),
            alternatives=alternatives,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Full analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SkyCoach API",
        "version": "1.0.0"
    }
