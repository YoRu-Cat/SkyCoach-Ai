from fastapi import APIRouter, HTTPException
from typing import List, Tuple
from datetime import datetime
import sys
import os
import shlex
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.ai_engine import (
    analyze_task_smart,
    get_demo_weather,
    get_weather,
    get_weather_by_city,
)
from services.maps import render_map
from services.chat_assistant import chat_assistant_reply
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
    ChatAssistantRequest,
    ChatAssistantResponse,
    BackendCliRequest,
    BackendCliResponse,
)

router = APIRouter(prefix="/api", tags=["analysis"])


def convert_task_to_response(task: TaskAnalysis) -> TaskAnalysisResponse:
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
    try:
        model_name = request.openai_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        task = analyze_task_smart(
            text=request.text,
            use_openai=request.use_openai,
            openai_api_key=request.openai_api_key,
            model=model_name,
        )
        
        return convert_task_to_response(task)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Task analysis failed: {str(e)}")


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
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
        model_name = request.openai_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        task = analyze_task_smart(
            text=request.activity_text,
            use_openai=request.use_openai,
            openai_api_key=request.openai_api_key,
            model=model_name,
        )
        
        weather_api_key = request.weather_api_key or os.getenv("OPENWEATHER_API_KEY")

        has_coordinates = request.latitude is not None and request.longitude is not None

        if request.use_demo_weather or not weather_api_key:
            weather = get_demo_weather(
                request.city,
                latitude=request.latitude if has_coordinates else None,
                longitude=request.longitude if has_coordinates else None,
            )
        else:
            if has_coordinates:
                weather = get_weather(request.latitude, request.longitude, weather_api_key)
            else:
                weather = get_weather_by_city(request.city, weather_api_key)
        
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


@router.post("/predict")
async def predict_activity_type(request: dict) -> dict:
    """Phase 5: Classify activity as Indoor/Outdoor/Mixed/Unclear using trained ML model."""
    try:
        from mlops.phase5.inference.inference import PredictionEngine
        from mlops.phase5.inference.schema import PredictionRequest
        
        phrase = request.get("phrase", "")
        if not phrase or not phrase.strip():
            raise ValueError("Phrase cannot be empty")
        
        artifacts_dir = Path("mlops/phase5/artifacts")
        if not artifacts_dir.exists():
            raise FileNotFoundError(
                f"ML artifacts not found. Run: python mlops/phase5/run_phase5.py"
            )
        
        engine = PredictionEngine(
            tokenizer_path=artifacts_dir / "phase4_tokenizer.json",
            model_path=artifacts_dir / "phase4_champion_model.json",
            report_path=artifacts_dir / "phase4_training_report.json",
            min_confidence=0.72,
        )
        
        pred_request = PredictionRequest(phrase=phrase)
        response = engine.predict(pred_request)
        
        return {
            "label": response.label,
            "confidence": response.confidence,
            "rationale": response.rationale,
            "model": response.model,
            "all_scores": response.all_scores,
        }
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=503,
            detail=f"ML service not initialized: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/chat-assistant", response_model=ChatAssistantResponse)
async def chat_assistant(request: ChatAssistantRequest) -> ChatAssistantResponse:
    try:
        model_name = request.openai_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        today_iso = request.today_iso or datetime.now().date().isoformat()
        reply = chat_assistant_reply(
            messages=[{"role": message.role, "content": message.content} for message in request.messages],
            draft={
                "task_title": request.draft.task_title,
                "date": request.draft.date,
                "time": request.draft.time,
                "notes": request.draft.notes,
            },
            task_context=[
                {
                    "id": task.id,
                    "title": task.title,
                    "completed": task.completed,
                    "scheduled_at": task.scheduled_at,
                }
                for task in request.task_context
            ],
            today_iso=today_iso,
            use_openai=request.use_openai,
            openai_api_key=request.openai_api_key,
            openai_model=model_name,
        )

        return ChatAssistantResponse(
            assistant_message=reply["assistant_message"],
            draft=reply["draft"],
            missing_fields=reply["missing_fields"],
            requires_confirmation=reply["requires_confirmation"],
            create_task=reply["create_task"],
            remove_task_id=reply.get("remove_task_id"),
            complete_task_id=reply.get("complete_task_id"),
            uncomplete_task_id=reply.get("uncomplete_task_id"),
            reschedule_task_id=reply.get("reschedule_task_id"),
            reschedule_date=reply.get("reschedule_date"),
            reschedule_time=reply.get("reschedule_time"),
            clear_completed=bool(reply.get("clear_completed", False)),
            navigate_to=reply["navigate_to"],
            reset_draft=reply["reset_draft"],
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chat assistant failed: {str(e)}")


@router.post("/backend-cli", response_model=BackendCliResponse)
async def backend_cli(request: BackendCliRequest) -> BackendCliResponse:
    """Safe backend command runner for frontend terminal UI.

    This endpoint intentionally avoids shell execution and supports only a
    constrained set of predefined commands.
    """
    command = request.command.strip()
    if not command:
        raise HTTPException(status_code=400, detail="Command is empty")

    try:
        parts = shlex.split(command)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f"Invalid command syntax: {str(exc)}")

    if not parts:
        raise HTTPException(status_code=400, detail="Command is empty")

    primary = parts[0].lower()
    now_iso = datetime.utcnow().isoformat() + "Z"

    help_text = "\n".join(
        [
            "SkyCoach Backend CLI",
            "Supported commands:",
            "- help: show this help",
            "- health: show backend health status",
            "- version: show API version",
            "- time: show server UTC time",
            "- weather <city>: fetch demo weather for city",
            "- analyze <activity text>: classify activity",
        ]
    )

    if primary == "help":
        return BackendCliResponse(
            command=command,
            output=help_text,
            ok=True,
            timestamp=now_iso,
        )

    if primary == "health":
        return BackendCliResponse(
            command=command,
            output="status=healthy service=SkyCoach API version=1.0.0",
            ok=True,
            timestamp=now_iso,
        )

    if primary == "version":
        return BackendCliResponse(
            command=command,
            output="SkyCoach API v1.0.0",
            ok=True,
            timestamp=now_iso,
        )

    if primary == "time":
        return BackendCliResponse(
            command=command,
            output=f"UTC {now_iso}",
            ok=True,
            timestamp=now_iso,
        )

    if primary == "weather":
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Usage: weather <city>")
        city = " ".join(parts[1:])
        weather = get_demo_weather(city)
        output = (
            f"city={weather.city}, condition={weather.condition}, temp={weather.temperature}{weather.temp_unit}, "
            f"rain_1h={weather.rain_1h}, wind_mph={weather.wind_mph:.1f}"
        )
        return BackendCliResponse(
            command=command,
            output=output,
            ok=True,
            timestamp=now_iso,
        )

    if primary == "analyze":
        if len(parts) < 2:
            raise HTTPException(status_code=400, detail="Usage: analyze <activity text>")
        activity_text = " ".join(parts[1:])
        task = analyze_task_smart(
            text=activity_text,
            use_openai=False,
            openai_api_key=None,
            model=os.getenv("OPENAI_MODEL") or "gpt-4o-mini",
        )
        output = (
            f"activity={task.activity}, classification={task.classification}, "
            f"confidence={task.confidence:.2f}"
        )
        return BackendCliResponse(
            command=command,
            output=output,
            ok=True,
            timestamp=now_iso,
        )

    raise HTTPException(
        status_code=400,
        detail="Unknown command. Try: help",
    )
