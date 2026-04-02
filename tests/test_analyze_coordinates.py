from fastapi.testclient import TestClient

from backend.main import app
from backend.api import routes
from models.data_classes import TaskAnalysis, WeatherData


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
