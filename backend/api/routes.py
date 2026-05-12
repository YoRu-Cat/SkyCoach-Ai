from fastapi import APIRouter, Depends, HTTPException, Request
from datetime import datetime, timezone
import sys
import os
import shlex

from backend.security import (
    assert_valid_coords,
    rate_limit_dependency,
    require_admin_token,
    safe_http_error,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from services.ai_engine import (
    analyze_task_smart,
    get_demo_weather,
    get_demo_weather_forecast,
    get_weather,
    get_weather_by_city,
    get_weather_forecast,
    get_weather_forecast_by_city,
)
from services.chat_assistant import chat_assistant_reply
from core.scoring_engine import (
    calculate_sky_score,
    get_alternative_activities,
    recommend_best_schedule,
)
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
        best_date=getattr(task, "best_date", None),
        best_time=getattr(task, "best_time", None),
        best_datetime_reason=getattr(task, "best_datetime_reason", None),
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


def _enrich_task_with_ml_suggestions(task: TaskAnalysis, input_text: str) -> None:
    """Attach robust suggestion fields from ML ranking without breaking primary analysis."""
    try:
        from ml_system.api import get_ml_system

        ml_result = get_ml_system().predict(input_text)
        suggestions = ml_result.get("suggestions", [])

        if suggestions:
            top = suggestions[0]
            if not task.suggested_classification:
                task.suggested_classification = top.get("label")
            if not getattr(task, "suggestion_confidence", 0.0):
                task.suggestion_confidence = float(top.get("confidence", 0.0))
    except Exception:
        pass


@router.post(
    "/analyze-task",
    response_model=TaskAnalysisResponse,
    dependencies=[
        Depends(rate_limit_dependency(requests=20, window_seconds=60)),
    ],
)
async def analyze_task(request: TaskAnalysisRequest) -> TaskAnalysisResponse:
    try:
        model_name = request.openai_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        task = analyze_task_smart(
            text=request.text,
            use_openai=request.use_openai,
            openai_api_key=request.openai_api_key,
            model=model_name,
        )

        _enrich_task_with_ml_suggestions(task, request.text)

        return convert_task_to_response(task)
    except Exception as e:
        raise safe_http_error(400, "Task analysis failed.", log_exception=e)


@router.post(
    "/weather",
    response_model=WeatherResponse,
    dependencies=[
        Depends(rate_limit_dependency(requests=60, window_seconds=60)),
    ],
)
async def get_weather(request: WeatherRequest) -> WeatherResponse:
    try:
        assert_valid_coords(request.latitude, request.longitude)
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
                raise HTTPException(status_code=400, detail="Provide either city name or coordinates.")

        return convert_weather_to_response(weather)
    except HTTPException:
        raise
    except Exception as e:
        raise safe_http_error(400, "Weather fetch failed.", log_exception=e)


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
        raise safe_http_error(400, "Score calculation failed.", log_exception=e)


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
        raise safe_http_error(400, "Could not get alternatives.", log_exception=e)


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    dependencies=[
        Depends(rate_limit_dependency(requests=10, window_seconds=60)),
    ],
)
async def full_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """End-to-end analysis: task, weather, score, alternatives."""
    try:
        assert_valid_coords(request.latitude, request.longitude)
        model_name = request.openai_model or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"
        task = analyze_task_smart(
            text=request.activity_text,
            use_openai=request.use_openai,
            openai_api_key=request.openai_api_key,
            model=model_name,
        )
        _enrich_task_with_ml_suggestions(task, request.activity_text)
        
        weather_api_key = request.weather_api_key or os.getenv("OPENWEATHER_API_KEY")

        has_coordinates = request.latitude is not None and request.longitude is not None
        forecast_slots = []

        if request.use_demo_weather or not weather_api_key:
            weather = get_demo_weather(
                request.city,
                latitude=request.latitude if has_coordinates else None,
                longitude=request.longitude if has_coordinates else None,
            )
            forecast_slots = get_demo_weather_forecast(request.city)
        else:
            if has_coordinates:
                weather = get_weather(request.latitude, request.longitude, weather_api_key)
                try:
                    forecast_slots = get_weather_forecast(
                        request.latitude,
                        request.longitude,
                        weather_api_key,
                    )
                except Exception:
                    forecast_slots = []
            else:
                weather = get_weather_by_city(request.city, weather_api_key)
                try:
                    forecast_slots = get_weather_forecast_by_city(request.city, weather_api_key)
                except Exception:
                    forecast_slots = []
        
        config = Config()
        score_result = calculate_sky_score(task, weather, config)
        best_date, best_time, best_reason = recommend_best_schedule(
            task,
            weather,
            forecast_slots=forecast_slots,
        )
        task.best_date = best_date
        task.best_time = best_time
        task.best_datetime_reason = best_reason
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
    except HTTPException:
        raise
    except Exception as e:
        raise safe_http_error(400, "Full analysis failed.", log_exception=e)


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "SkyCoach API",
        "version": "1.0.0"
    }


VALID_LABELS = {"Indoor", "Outdoor", "Mixed", "Unclear"}
MAX_PREDICT_PHRASE = 2000


@router.post(
    "/predict",
    dependencies=[
        Depends(rate_limit_dependency(requests=60, window_seconds=60)),
    ],
)
async def predict_activity_type(request: dict) -> dict:
    """Classify activity as Indoor/Outdoor/Mixed/Unclear using unified ML system."""
    try:
        from ml_system.api import get_ml_system

        phrase = (request.get("phrase") or "").strip()
        if not phrase:
            raise HTTPException(status_code=400, detail="Phrase cannot be empty.")
        if len(phrase) > MAX_PREDICT_PHRASE:
            raise HTTPException(status_code=400, detail="Phrase too long.")

        ml_system = get_ml_system()
        result = ml_system.predict(phrase)

        return {
            **result,
            "predicted_label": result.get("label"),
            "predicted_confidence": result.get("confidence"),
        }
    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise safe_http_error(503, "ML service not initialized.", log_exception=e)
    except Exception as e:
        raise safe_http_error(400, "Prediction failed.", log_exception=e)


@router.post(
    "/feedback",
    dependencies=[
        Depends(rate_limit_dependency(requests=10, window_seconds=60)),
    ],
)
async def submit_prediction_feedback(request: dict) -> dict:
    """Record a user correction. Does not retrain by itself: retraining is
    triggered explicitly by the model-refresh flow.

    ``corrected_label`` must be one of the four canonical labels, ``phrase``
    must be non-empty (max ``MAX_PREDICT_PHRASE``), and confidence must be
    in [0, 1].
    """
    try:
        from ml_system.api import get_ml_system

        phrase = (request.get("phrase") or "").strip()
        predicted_label = (request.get("predicted_label") or request.get("label") or "").strip()
        corrected_label = (request.get("corrected_label") or "").strip()

        try:
            predicted_confidence = float(
                request.get("predicted_confidence", request.get("confidence", 0.0))
            )
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail="Confidence must be numeric.")

        if not (phrase and predicted_label and corrected_label):
            raise HTTPException(
                status_code=400,
                detail="Missing required fields: phrase, predicted_label, corrected_label.",
            )
        if len(phrase) > MAX_PREDICT_PHRASE:
            raise HTTPException(status_code=400, detail="Phrase too long.")
        if predicted_label not in VALID_LABELS or corrected_label not in VALID_LABELS:
            raise HTTPException(
                status_code=400,
                detail=f"Labels must be one of {sorted(VALID_LABELS)}.",
            )
        if not (0.0 <= predicted_confidence <= 1.0):
            raise HTTPException(status_code=400, detail="Confidence must be in [0, 1].")

        ml_system = get_ml_system()
        return ml_system.submit_feedback(
            phrase=phrase,
            predicted=predicted_label,
            confidence=predicted_confidence,
            corrected=corrected_label,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise safe_http_error(400, "Feedback submission failed.", log_exception=e)


@router.get("/model-comparison")
async def get_model_comparison(
    request: Request,
    refresh: bool = False,
) -> dict:
    """Return the head-to-head evaluation report for the two models.

    Reads ``ml_system/models/current/evaluation_report.json``. Pass
    ``refresh=true`` to regenerate; gated by ``X-Admin-Token`` when
    ``ADMIN_API_TOKEN`` is set.
    """
    try:
        import json as _json
        from ml_system.config.settings import CONFIG as _CONFIG

        report_path = _CONFIG.get_current_model_path() / "evaluation_report.json"

        if refresh:
            require_admin_token(request)
            from ml_system.training.evaluation import run_evaluation
            return run_evaluation(output_path=report_path)

        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Evaluation report not yet generated.")

        return _json.loads(report_path.read_text(encoding="utf-8"))
    except HTTPException:
        raise
    except Exception as e:
        raise safe_http_error(400, "Model comparison failed.", log_exception=e)


@router.get("/learning-status")
async def get_learning_status() -> dict:
    """Get continuous learning system status."""
    try:
        from ml_system.api import get_ml_system

        status = get_ml_system().get_status()

        return {
            "feedback_records": status["feedback_records"],
            "uncertain_predictions": status["uncertain_predictions"],
            "total_new_data": status["total_new_data"],
            "should_retrain": status["should_retrain"],
            "active_model_version": status["active_model_version"],
            "active_model_test_f1": status["active_model_test_f1"],
            "model_versions_count": status["model_versions_count"],
            "drift_alert_count": status["drift_alert_count"],
        }
    except Exception as e:
        raise safe_http_error(400, "Learning status query failed.", log_exception=e)


@router.post(
    "/chat-assistant",
    response_model=ChatAssistantResponse,
    dependencies=[
        Depends(rate_limit_dependency(requests=15, window_seconds=60)),
    ],
)
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

        # Only allow task IDs the client itself sent in task_context.
        # Drops anything the model fabricates outside that set.
        allowed_ids = {task.id for task in request.task_context}

        def whitelist(value):
            return value if value in allowed_ids else None

        return ChatAssistantResponse(
            assistant_message=reply["assistant_message"],
            draft=reply["draft"],
            missing_fields=reply["missing_fields"],
            requires_confirmation=reply["requires_confirmation"],
            create_task=reply["create_task"],
            remove_task_id=whitelist(reply.get("remove_task_id")),
            complete_task_id=whitelist(reply.get("complete_task_id")),
            uncomplete_task_id=whitelist(reply.get("uncomplete_task_id")),
            reschedule_task_id=whitelist(reply.get("reschedule_task_id")),
            reschedule_date=reply.get("reschedule_date"),
            reschedule_time=reply.get("reschedule_time"),
            clear_completed=bool(reply.get("clear_completed", False)),
            navigate_to=reply["navigate_to"],
            reset_draft=reply["reset_draft"],
        )
    except Exception as e:
        raise safe_http_error(400, "Chat assistant failed.", log_exception=e)


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
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

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
