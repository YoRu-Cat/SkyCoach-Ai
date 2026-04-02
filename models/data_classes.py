from dataclasses import dataclass, field
from typing import Literal, Optional, List


@dataclass
class Config:
    openai_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    weather_units: str = "metric"
    
    rain_threshold: float = 0.0
    wind_threshold_mph: float = 15.0
    heat_threshold_c: float = 30.0
    
    outdoor_rain_penalty: int = -80
    outdoor_wind_penalty: int = -30
    indoor_rain_bonus: int = 20
    indoor_heat_bonus: int = 10


@dataclass
class TaskAnalysis:
    original_text: str
    cleaned_text: str
    activity: str
    classification: Literal["Indoor", "Outdoor"]
    confidence: float
    reasoning: str
    needs_clarification: bool = False
    issue: Optional[str] = None
    suggested_activity: Optional[str] = None
    suggested_classification: Optional[str] = None
    suggestion_confidence: float = 0.0


@dataclass
class HistoryEntry:
    timestamp: str
    activity: str
    classification: str
    score: int
    city: str
    weather_condition: str


@dataclass
class WeatherData:
    city: str
    country: str
    latitude: float
    longitude: float
    temperature: float
    feels_like: float
    humidity: int
    rain_1h: float
    is_raining: bool
    wind_speed: float
    wind_mph: float
    condition: str
    description: str
    icon_code: str
    units: str
    
    @property
    def temp_unit(self) -> str:
        return "°C" if self.units == "metric" else "°F"
    
    @property
    def temp_celsius(self) -> float:
        if self.units == "imperial":
            return (self.temperature - 32) * 5/9
        return self.temperature
    
    def get_emoji(self) -> str:
        emojis = {
            "Clear": "☀️", "Clouds": "☁️", "Rain": "🌧️",
            "Drizzle": "🌦️", "Thunderstorm": "⛈️", "Snow": "❄️",
            "Mist": "🌫️", "Fog": "🌫️"
        }
        return emojis.get(self.condition, "🌡️")


@dataclass
class SkyScoreResult:
    score: int
    classification: str
    weather_factors: list
    bonuses: list
    penalties: list
    recommendation: str
