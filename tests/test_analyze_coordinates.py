from fastapi.testclient import TestClient

from backend.main import app
from backend.api import routes
from models.data_classes import TaskAnalysis, WeatherData
from services import ai_engine


client = TestClient(app)


def _sample_task() -> TaskAnalysis:
    return TaskAnalysis(
        original_text="playing soccer",
        cleaned_text="Playing Soccer",
        activity="playing soccer",
        classification="Outdoor",
        confidence=0.91,
        reasoning="Detected as outdoor activity",
        needs_clarification=False,
    )


def _sample_weather(city: str = "GPS City") -> WeatherData:
    return WeatherData(
        city=city,
        country="US",
        latitude=37.7749,
        longitude=-122.4194,
        temperature=18.2,
        feels_like=17.0,
        humidity=62,
        rain_1h=0.0,
        is_raining=False,
        wind_speed=4.1,
        wind_mph=9.2,
        condition="Clouds",
        description="scattered clouds",
        icon_code="03d",
        units="metric",
    )


def test_analyze_uses_coordinates_when_provided(monkeypatch):
    called = {"coords": False, "city": False}

    def fake_analyze_task_smart(*args, **kwargs):
        return _sample_task()

    def fake_get_weather(lat, lon, api_key):
        assert lat == 40.7128
        assert lon == -74.0060
        assert api_key == "test-weather-key"
        called["coords"] = True
        return _sample_weather(city="Coordinate City")

    def fake_get_weather_by_city(*args, **kwargs):
        called["city"] = True
        raise AssertionError("City weather lookup should not be called when coordinates are present")

    monkeypatch.setattr(routes, "analyze_task_smart", fake_analyze_task_smart)
    monkeypatch.setattr(routes, "get_weather", fake_get_weather)
    monkeypatch.setattr(routes, "get_weather_by_city", fake_get_weather_by_city)

    response = client.post(
        "/api/analyze",
        json={
            "activity_text": "playing soccer",
            "city": "New York",
            "latitude": 40.7128,
            "longitude": -74.0060,
            "use_openai": False,
            "weather_api_key": "test-weather-key",
            "use_demo_weather": False,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["weather"]["city"] == "Coordinate City"
    assert called["coords"] is True
    assert called["city"] is False


def test_analyze_preserves_coordinates_in_demo_weather(monkeypatch):
    def fake_analyze_task_smart(*args, **kwargs):
        return _sample_task()

    monkeypatch.setattr(routes, "analyze_task_smart", fake_analyze_task_smart)

    response = client.post(
        "/api/analyze",
        json={
            "activity_text": "playing soccer",
            "city": "New York",
            "latitude": 51.5074,
            "longitude": -0.1278,
            "use_openai": False,
            "weather_api_key": None,
            "use_demo_weather": True,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["weather"]["latitude"] == 51.5074
    assert payload["weather"]["longitude"] == -0.1278


def test_analyze_task_smart_uses_openai_when_requested(monkeypatch):
    calls = {"openai": 0, "fallback": 0}

    def fake_openai(text: str, api_key: str, model: str = "gpt-4o-mini"):
        calls["openai"] += 1
        return TaskAnalysis(
            original_text=text,
            cleaned_text="Going to Gym",
            activity="going to gym",
            classification="Outdoor",
            confidence=0.97,
            reasoning="OpenAI judged gym as outdoor",
            needs_clarification=False,
            suggestion_confidence=0.0,
        )

    def fake_fallback(text: str):
        calls["fallback"] += 1
        return _sample_task()

    monkeypatch.setattr(ai_engine, "analyze_task_openai", fake_openai)
    monkeypatch.setattr(ai_engine, "analyze_task_fallback", fake_fallback)
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    result = ai_engine.analyze_task_smart("Going to gym", use_openai=True)

    assert result.classification == "Outdoor"
    assert calls["openai"] == 1
    assert calls["fallback"] == 0


def test_analyze_task_smart_falls_back_when_key_is_missing(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    result = ai_engine.analyze_task_smart("Going to gym", use_openai=True)

    assert result.classification == "Outdoor"
    assert "cross-validation" in result.reasoning


def test_analyze_task_fallback_classifies_gym_as_outdoor():
    result = ai_engine.analyze_task_smart("Going to gym", use_openai=False)
    assert result.classification == "Outdoor"


def test_detect_input_issue_allows_going_to_gym_phrase():
    needs_clarification, issue = ai_engine._detect_input_issue(
        "going to gym",
        outdoor_score=0,
        indoor_score=0,
    )
    assert needs_clarification is False
    assert issue is None


def test_detect_input_issue_allows_going_to_work_phrase():
    needs_clarification, issue = ai_engine._detect_input_issue(
        "going to work",
        outdoor_score=0,
        indoor_score=0,
    )
    assert needs_clarification is False
    assert issue is None


def test_rulejudge_prefers_outdoor_for_work_then_gym():
    result = ai_engine.analyze_task_smart("going to work then gym", use_openai=False)
    assert result.classification == "Outdoor"


def test_rulejudge_keeps_going_to_work_indoor():
    result = ai_engine.analyze_task_smart("going to work", use_openai=False)
    assert result.classification == "Indoor"


def test_rulejudge_treats_going_to_work_outside_as_outdoor():
    result = ai_engine.analyze_task_smart("going to work outside", use_openai=False)
    assert result.classification == "Outdoor"


def test_openai_verification_can_correct_local_indoor_judgment(monkeypatch):
    responses = iter(
        [
            {"cleaned_text": "going to uni", "activity": "going to uni"},
            {
                "classification": "Outdoor",
                "confidence": 0.93,
                "reasoning": "Going to uni is a commute, not an indoor activity.",
                "corrected_activity": "going to uni",
            },
        ]
    )

    def fake_openai_json_response(*args, **kwargs):
        return next(responses)

    def fake_classify_with_dictionary(*args, **kwargs):
        return "Indoor", 0.81, "token-prior consensus"

    def fake_auto_judge_input(*args, **kwargs):
        return {
            "is_broken": False,
            "suggestion": None,
            "confidence": 0.0,
            "classification": None,
        }

    monkeypatch.setattr(ai_engine, "_openai_json_response", fake_openai_json_response)
    monkeypatch.setattr(ai_engine, "classify_with_dictionary", fake_classify_with_dictionary)
    monkeypatch.setattr(ai_engine, "auto_judge_input", fake_auto_judge_input)

    result = ai_engine.analyze_task_openai("going to uni", api_key="test-key")

    assert result.classification == "Outdoor"
    assert "verification corrected" in result.reasoning.lower()
