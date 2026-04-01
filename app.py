"""
🌤️ SkyCoach AI - Beautiful Weather-Based Activity Advisor
=========================================================

A stunning Streamlit application with:
- OpenAI-powered text understanding
- Real-time weather from OpenWeatherMap  
- Interactive Folium maps
- Animated SkyScore gauge
- Glassmorphism UI with smooth animations

Run with: streamlit run app.py
"""

import streamlit as st
import requests
import json
import folium
from streamlit_folium import st_folium
from dataclasses import dataclass, field
from typing import Literal, Optional, List
from datetime import datetime
import time
import hashlib


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class Config:
    """Central configuration for API keys and settings."""
    openai_api_key: Optional[str] = None
    openweather_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"
    weather_units: str = "metric"
    
    # Scoring thresholds
    rain_threshold: float = 0.0
    wind_threshold_mph: float = 15.0
    heat_threshold_c: float = 30.0
    
    # Scoring weights
    outdoor_rain_penalty: int = -80
    outdoor_wind_penalty: int = -30
    indoor_rain_bonus: int = 20
    indoor_heat_bonus: int = 10


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TaskAnalysis:
    """Result of language analysis."""
    original_text: str
    cleaned_text: str
    activity: str
    classification: Literal["Indoor", "Outdoor"]
    confidence: float
    reasoning: str


@dataclass
class HistoryEntry:
    """A saved analysis entry."""
    timestamp: str
    activity: str
    classification: str
    score: int
    city: str
    weather_condition: str


@dataclass  
class WeatherData:
    """Weather information from API."""
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
    """Final scoring result."""
    score: int
    classification: str
    weather_factors: list
    bonuses: list
    penalties: list
    recommendation: str


# ============================================================================
# LANGUAGE ENGINE
# ============================================================================

def analyze_task_openai(text: str, api_key: str, model: str = "gpt-4o-mini") -> TaskAnalysis:
    """Use OpenAI to analyze and classify the task."""
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are SkyCoach's Task Analysis Engine. Analyze the user's activity and respond in JSON:
{
    "cleaned_text": "Corrected text",
    "activity": "Core activity (2-4 words)",
    "classification": "Indoor" or "Outdoor",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation"
}

OUTDOOR: gardening, car washing, jogging, hiking, cycling, sports, yard work, BBQ, pool
INDOOR: cooking, reading, gaming, cleaning, working, studying, yoga indoors, crafts"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze: {text}"}
        ],
        response_format={"type": "json_object"},
        max_tokens=150,
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    
    return TaskAnalysis(
        original_text=text,
        cleaned_text=result.get("cleaned_text", text),
        activity=result.get("activity", "Unknown"),
        classification=result.get("classification", "Indoor"),
        confidence=float(result.get("confidence", 0.8)),
        reasoning=result.get("reasoning", "")
    )


def analyze_task_fallback(text: str) -> TaskAnalysis:
    """Keyword-based fallback when API unavailable."""
    text_lower = text.lower()
    
    outdoor_keywords = ["car", "wash", "garden", "jog", "run", "hike", "bike", 
                       "walk", "dog", "picnic", "bbq", "swim", "yard", "lawn",
                       "paint outside", "sport", "tennis", "golf", "park", "outside"]
    indoor_keywords = ["cook", "read", "clean", "computer", "work", "study",
                      "watch", "game", "craft", "laundry", "yoga", "inside", "home"]
    
    outdoor_score = sum(1 for kw in outdoor_keywords if kw in text_lower)
    indoor_score = sum(1 for kw in indoor_keywords if kw in text_lower)
    
    if outdoor_score > indoor_score:
        classification = "Outdoor"
        confidence = min(0.75, 0.5 + outdoor_score * 0.1)
    else:
        classification = "Indoor"
        confidence = min(0.75, 0.5 + indoor_score * 0.1)
    
    return TaskAnalysis(
        original_text=text,
        cleaned_text=text.title(),
        activity=text[:30],
        classification=classification,
        confidence=confidence,
        reasoning="Classified using keyword matching (Demo Mode)"
    )


# ============================================================================
# WEATHER ENGINE  
# ============================================================================

def get_weather(lat: float, lon: float, api_key: str, units: str = "metric") -> WeatherData:
    """Fetch weather from OpenWeatherMap API."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": units}
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    rain = data.get("rain", {})
    rain_1h = rain.get("1h", 0.0)
    weather = data.get("weather", [{}])[0]
    wind_speed = data.get("wind", {}).get("speed", 0)
    wind_mph = wind_speed * 2.237 if units == "metric" else wind_speed
    
    return WeatherData(
        city=data.get("name", "Unknown"),
        country=data.get("sys", {}).get("country", ""),
        latitude=data["coord"]["lat"],
        longitude=data["coord"]["lon"],
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        rain_1h=rain_1h,
        is_raining=rain_1h > 0 or weather.get("main") in ["Rain", "Drizzle", "Thunderstorm"],
        wind_speed=wind_speed,
        wind_mph=wind_mph,
        condition=weather.get("main", "Unknown"),
        description=weather.get("description", ""),
        icon_code=weather.get("icon", "01d"),
        units=units
    )


def get_weather_by_city(city: str, api_key: str, units: str = "metric") -> WeatherData:
    """Fetch weather by city name."""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": units}
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    
    rain = data.get("rain", {})
    rain_1h = rain.get("1h", 0.0)
    weather = data.get("weather", [{}])[0]
    wind_speed = data.get("wind", {}).get("speed", 0)
    wind_mph = wind_speed * 2.237 if units == "metric" else wind_speed
    
    return WeatherData(
        city=data.get("name", "Unknown"),
        country=data.get("sys", {}).get("country", ""),
        latitude=data["coord"]["lat"],
        longitude=data["coord"]["lon"],
        temperature=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        humidity=data["main"]["humidity"],
        rain_1h=rain_1h,
        is_raining=rain_1h > 0 or weather.get("main") in ["Rain", "Drizzle", "Thunderstorm"],
        wind_speed=wind_speed,
        wind_mph=wind_mph,
        condition=weather.get("main", "Unknown"),
        description=weather.get("description", ""),
        icon_code=weather.get("icon", "01d"),
        units=units
    )


def get_demo_weather(city: str = "New York") -> WeatherData:
    """Demo weather data for testing without API - deterministic based on city."""
    # Create deterministic "random" based on city name for consistency
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)
    
    # Predefined weather scenarios
    scenarios = [
        ("Clear", "clear sky", "01d", False, 0.0, 26.0),
        ("Clouds", "scattered clouds", "03d", False, 0.0, 22.0),
        ("Rain", "light rain", "10d", True, 2.5, 18.0),
        ("Clouds", "overcast clouds", "04d", False, 0.0, 20.0),
        ("Clear", "sunny", "01d", False, 0.0, 32.0),  # Hot day
    ]
    
    # Select scenario based on city hash
    scenario_idx = city_hash % len(scenarios)
    condition, desc, icon, is_rain, rain_amt, base_temp = scenarios[scenario_idx]
    
    # Slight variations based on hash
    temp_var = (city_hash % 10) - 5  # -5 to +4
    wind_base = 3 + (city_hash % 15)  # 3 to 17 m/s
    humidity = 40 + (city_hash % 40)  # 40-79%
    
    # City coordinates (approximate)
    city_coords = {
        "new york": (40.7128, -74.0060),
        "london": (51.5074, -0.1278),
        "tokyo": (35.6762, 139.6503),
        "paris": (48.8566, 2.3522),
        "sydney": (-33.8688, 151.2093),
        "los angeles": (34.0522, -118.2437),
        "dubai": (25.2048, 55.2708),
        "mumbai": (19.0760, 72.8777),
    }
    
    lat, lon = city_coords.get(city.lower(), (40.7128, -74.0060))
    
    temp = base_temp + temp_var
    wind_mph = wind_base * 2.237
    
    return WeatherData(
        city=city.title(),
        country="DEMO",
        latitude=lat,
        longitude=lon,
        temperature=round(temp, 1),
        feels_like=round(temp - 2, 1),
        humidity=humidity,
        rain_1h=rain_amt,
        is_raining=is_rain,
        wind_speed=round(wind_base, 1),
        wind_mph=round(wind_mph, 1),
        condition=condition,
        description=desc,
        icon_code=icon,
        units="metric"
    )


# ============================================================================
# SCORING ENGINE
# ============================================================================

def calculate_sky_score(task: TaskAnalysis, weather: WeatherData, config: Config) -> SkyScoreResult:
    """
    Calculate the SkyScore using the Decision Matrix.
    
    Decision Matrix:
    - Outdoor + Rain > 0mm → -80%
    - Outdoor + Wind > 15mph → -30%
    - Indoor + Rain > 0mm → +20%
    - Indoor + Temp > 30°C → +10%
    """
    score = 100
    bonuses = []
    penalties = []
    factors = []
    
    # Check rain
    if weather.is_raining or weather.rain_1h > config.rain_threshold:
        factors.append(f"🌧️ Rain: {weather.rain_1h:.1f}mm/h")
        if task.classification == "Outdoor":
            score += config.outdoor_rain_penalty
            penalties.append(("Rain detected", config.outdoor_rain_penalty, "Outdoor activities not recommended in rain"))
        else:
            score += config.indoor_rain_bonus
            bonuses.append(("Perfect rain weather", config.indoor_rain_bonus, "Great time for indoor activities!"))
    
    # Check wind
    if weather.wind_mph > config.wind_threshold_mph:
        factors.append(f"💨 Wind: {weather.wind_mph:.1f} mph")
        if task.classification == "Outdoor":
            score += config.outdoor_wind_penalty
            penalties.append(("High winds", config.outdoor_wind_penalty, "Wind may affect outdoor activities"))
    
    # Check temperature
    temp_c = weather.temp_celsius if hasattr(weather, 'temp_celsius') else weather.temperature
    if temp_c > config.heat_threshold_c:
        factors.append(f"🌡️ Hot: {weather.temperature:.1f}{weather.temp_unit}")
        if task.classification == "Indoor":
            score += config.indoor_heat_bonus
            bonuses.append(("Hot outside", config.indoor_heat_bonus, "Good choice staying indoors with AC"))
    
    # Add neutral weather factors
    if not weather.is_raining and weather.rain_1h <= 0:
        factors.append(f"☀️ No rain")
    if weather.wind_mph <= config.wind_threshold_mph:
        factors.append(f"🍃 Light wind: {weather.wind_mph:.1f} mph")
    
    # Clamp score
    score = max(0, min(100, score))
    
    # Generate recommendation
    if score >= 80:
        recommendation = "🎉 Perfect conditions! Go ahead with your activity."
    elif score >= 60:
        recommendation = "👍 Good conditions with minor considerations."
    elif score >= 40:
        recommendation = "⚠️ Moderate conditions. Consider alternatives."
    elif score >= 20:
        recommendation = "🔶 Poor conditions. Postpone if possible."
    else:
        recommendation = "❌ Not recommended. Choose a different activity."
    
    return SkyScoreResult(
        score=score,
        classification=task.classification,
        weather_factors=factors,
        bonuses=bonuses,
        penalties=penalties,
        recommendation=recommendation
    )


# ============================================================================
# STREAMLIT UI - STYLES & ANIMATIONS
# ============================================================================

def inject_custom_css():
    """Inject beautiful custom CSS with glassmorphism and animations."""
    st.markdown("""
    <style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    /* Root variables */
    :root {
        --primary: #6366f1;
        --primary-dark: #4f46e5;
        --secondary: #8b5cf6;
        --accent: #06b6d4;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --bg-dark: #0f0f1a;
        --bg-card: rgba(255, 255, 255, 0.05);
        --text-primary: #ffffff;
        --text-secondary: rgba(255, 255, 255, 0.7);
        --glass-bg: rgba(255, 255, 255, 0.08);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Glass card */
    .glass-card {
        background: var(--glass-bg);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        animation: fadeInUp 0.6s ease-out forwards;
    }
    
    /* Hero section */
    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: gradientShift 3s ease infinite;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: var(--text-secondary);
        text-align: center;
        margin-bottom: 2rem;
    }
    
    /* Score circle */
    .score-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .score-circle {
        position: relative;
        width: 200px;
        height: 200px;
        border-radius: 50%;
        background: conic-gradient(
            var(--primary) calc(var(--score) * 3.6deg),
            rgba(255, 255, 255, 0.1) 0deg
        );
        display: flex;
        justify-content: center;
        align-items: center;
        animation: pulse 2s ease-in-out infinite;
    }
    
    .score-inner {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        background: var(--bg-dark);
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        box-shadow: inset 0 0 30px rgba(0, 0, 0, 0.5);
    }
    
    .score-value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3.5rem;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
    }
    
    .score-label {
        font-size: 0.9rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    /* Weather card */
    .weather-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.1) 100%);
        border-radius: 20px;
        padding: 1.5rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .weather-temp {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 3rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    
    .weather-condition {
        font-size: 1.2rem;
        color: var(--text-secondary);
    }
    
    .weather-emoji {
        font-size: 4rem;
        animation: bounce 2s ease-in-out infinite;
    }
    
    /* Status pill */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    
    .status-outdoor {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-indoor {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
    }
    
    /* Factor cards */
    .factor-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid var(--primary);
        transition: transform 0.2s ease;
    }
    
    .factor-card:hover {
        transform: translateX(5px);
    }
    
    .bonus-card {
        border-left-color: var(--success);
        background: rgba(16, 185, 129, 0.1);
    }
    
    .penalty-card {
        border-left-color: var(--danger);
        background: rgba(239, 68, 68, 0.1);
    }
    
    /* Input styling */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 16px !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 20px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 15, 26, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: var(--text-secondary);
    }
    
    /* Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            transform: scale(1);
        }
        50% {
            transform: scale(1.02);
        }
    }
    
    @keyframes bounce {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
    
    @keyframes gradientShift {
        0%, 100% {
            filter: hue-rotate(0deg);
        }
        50% {
            filter: hue-rotate(15deg);
        }
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .hero-title {
            font-size: 2.5rem;
        }
        .score-circle {
            width: 160px;
            height: 160px;
        }
        .score-inner {
            width: 130px;
            height: 130px;
        }
        .score-value {
            font-size: 2.5rem;
        }
    }
    
    /* Skeleton loading animation */
    .skeleton {
        background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.1) 50%, rgba(255,255,255,0.05) 75%);
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: 8px;
    }
    
    @keyframes shimmer {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    
    /* History card */
    .history-item {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin: 0.5rem 0;
        border-left: 3px solid var(--primary);
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.2s ease;
    }
    
    .history-item:hover {
        background: rgba(255, 255, 255, 0.06);
        transform: translateX(5px);
    }
    
    /* Alternative activities */
    .alt-activity {
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.1) 0%, rgba(99, 102, 241, 0.1) 100%);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 1px solid rgba(6, 182, 212, 0.2);
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .alt-activity:hover {
        border-color: var(--accent);
        transform: scale(1.02);
    }
    
    /* Forecast mini cards */
    .forecast-item {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 0.75rem;
        text-align: center;
        min-width: 80px;
    }
    </style>
    """, unsafe_allow_html=True)


def inject_gsap_animations():
    """Inject CSS-only animations (more reliable than GSAP in Streamlit)."""
    # GSAP doesn't work reliably in Streamlit due to how it renders
    # Using pure CSS animations instead
    st.markdown("""
    <style>
    /* Entry animations using CSS */
    .glass-card {
        animation: slideUp 0.6s ease-out forwards;
    }
    
    .glass-card:nth-child(1) { animation-delay: 0s; }
    .glass-card:nth-child(2) { animation-delay: 0.1s; }
    .glass-card:nth-child(3) { animation-delay: 0.2s; }
    .glass-card:nth-child(4) { animation-delay: 0.3s; }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Score counter animation */
    .score-value {
        animation: countUp 1s ease-out forwards;
    }
    
    @keyframes countUp {
        from { opacity: 0; transform: scale(0.5); }
        to { opacity: 1; transform: scale(1); }
    }
    
    /* Weather emoji bounce */
    .weather-emoji {
        animation: bounce 2s ease-in-out infinite;
    }
    
    /* Pulse effect for score circle */
    .score-circle {
        animation: pulse 2s ease-in-out infinite;
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================================================
# UI COMPONENTS
# ============================================================================

def render_hero():
    """Render the hero section."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0 2rem 0;">
        <h1 class="hero-title">🌤️ SkyCoach AI</h1>
        <p class="hero-subtitle">Your intelligent weather-based activity advisor</p>
    </div>
    """, unsafe_allow_html=True)


def render_score_gauge(score: int, classification: str):
    """Render the animated SkyScore gauge."""
    
    # Determine color based on score
    if score >= 80:
        color = "#10b981"  # Green
    elif score >= 60:
        color = "#06b6d4"  # Cyan
    elif score >= 40:
        color = "#f59e0b"  # Yellow
    elif score >= 20:
        color = "#f97316"  # Orange
    else:
        color = "#ef4444"  # Red
    
    st.markdown(f"""
    <div class="glass-card">
        <div class="score-container">
            <div class="score-circle" style="background: conic-gradient({color} {score * 3.6}deg, rgba(255,255,255,0.1) 0deg);">
                <div class="score-inner">
                    <span class="score-value">{score}</span>
                    <span class="score-label">SkyScore</span>
                </div>
            </div>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span class="status-pill status-{classification.lower()}">{classification} Activity</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_weather_card(weather: WeatherData):
    """Render the weather information card."""
    st.markdown(f"""
    <div class="glass-card weather-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div class="weather-temp">{weather.temperature:.1f}{weather.temp_unit}</div>
                <div class="weather-condition">{weather.description.title()}</div>
                <div style="color: rgba(255,255,255,0.5); margin-top: 0.5rem;">
                    📍 {weather.city}, {weather.country}
                </div>
            </div>
            <div class="weather-emoji">{weather.get_emoji()}</div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 1.5rem; text-align: center;">
            <div>
                <div style="font-size: 1.5rem;">💨</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.wind_mph:.1f} mph</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Wind</div>
            </div>
            <div>
                <div style="font-size: 1.5rem;">💧</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.humidity}%</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Humidity</div>
            </div>
            <div>
                <div style="font-size: 1.5rem;">🌧️</div>
                <div style="color: rgba(255,255,255,0.7);">{weather.rain_1h:.1f} mm</div>
                <div style="font-size: 0.8rem; color: rgba(255,255,255,0.4);">Rain</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_analysis_card(task: TaskAnalysis):
    """Render the task analysis card."""
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">🧠 Activity Analysis</h3>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">ORIGINAL INPUT</div>
            <div style="color: white;">"{task.original_text}"</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">CLEANED & UNDERSTOOD</div>
            <div style="color: white;">"{task.cleaned_text}"</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">IDENTIFIED ACTIVITY</div>
            <div style="color: white; font-weight: 600;">{task.activity}</div>
        </div>
        <div class="factor-card">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.8rem;">CLASSIFICATION ({task.confidence*100:.0f}% confidence)</div>
            <div style="color: white;">{task.reasoning}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_factors_card(result: SkyScoreResult):
    """Render the scoring factors card."""
    # Build all HTML content first
    factors_html = ""
    
    # Weather factors
    for factor in result.weather_factors:
        factors_html += f'''
        <div class="factor-card">
            <div style="color: white;">{factor}</div>
        </div>
        '''
    
    # Bonuses
    for name, value, desc in result.bonuses:
        factors_html += f'''
        <div class="factor-card bonus-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: white;">✅ {name}</div>
                <div style="color: #10b981; font-weight: 600;">+{value}%</div>
            </div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{desc}</div>
        </div>
        '''
    
    # Penalties
    for name, value, desc in result.penalties:
        factors_html += f'''
        <div class="factor-card penalty-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="color: white;">❌ {name}</div>
                <div style="color: #ef4444; font-weight: 600;">{value}%</div>
            </div>
            <div style="color: rgba(255,255,255,0.5); font-size: 0.85rem;">{desc}</div>
        </div>
        '''
    
    # Complete card with recommendation
    st.markdown(f"""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">📊 Scoring Factors</h3>
        {factors_html}
        <div style="margin-top: 1.5rem; padding: 1rem; background: rgba(99, 102, 241, 0.2); border-radius: 12px; text-align: center;">
            <div style="color: white; font-size: 1.1rem;">{result.recommendation}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_map(lat: float, lon: float, city: str, weather: WeatherData):
    """Render interactive Folium map with weather overlay."""
    
    # Create map centered on location
    m = folium.Map(
        location=[lat, lon],
        zoom_start=10,
        tiles="CartoDB dark_matter"
    )
    
    # Add weather marker
    popup_html = f"""
    <div style="font-family: 'Inter', sans-serif; padding: 10px;">
        <h4 style="margin: 0 0 10px 0;">{weather.get_emoji()} {city}</h4>
        <p style="margin: 5px 0;"><b>Temperature:</b> {weather.temperature:.1f}{weather.temp_unit}</p>
        <p style="margin: 5px 0;"><b>Condition:</b> {weather.description.title()}</p>
        <p style="margin: 5px 0;"><b>Wind:</b> {weather.wind_mph:.1f} mph</p>
        <p style="margin: 5px 0;"><b>Humidity:</b> {weather.humidity}%</p>
    </div>
    """
    
    # Custom icon color based on weather
    if weather.is_raining:
        icon_color = "blue"
    elif weather.condition == "Clear":
        icon_color = "orange"
    else:
        icon_color = "gray"
    
    folium.Marker(
        [lat, lon],
        popup=folium.Popup(popup_html, max_width=250),
        tooltip=f"{city}: {weather.temperature:.1f}{weather.temp_unit}",
        icon=folium.Icon(color=icon_color, icon="cloud", prefix="fa")
    ).add_to(m)
    
    # Add circle for visual effect
    folium.Circle(
        [lat, lon],
        radius=5000,
        color="#6366f1",
        fill=True,
        fill_opacity=0.2
    ).add_to(m)
    
    return m


def render_sidebar():
    """Render the sidebar with settings."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: white;">⚙️ Settings</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # API Keys section
        st.markdown("### 🔑 API Keys")
        
        openai_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get("openai_api_key", ""),
            help="Get your key at platform.openai.com"
        )
        
        weather_key = st.text_input(
            "OpenWeatherMap Key",
            type="password",
            value=st.session_state.get("openweather_api_key", ""),
            help="Get your free key at openweathermap.org"
        )
        
        # Save to session state
        if openai_key:
            st.session_state.openai_api_key = openai_key
        if weather_key:
            st.session_state.openweather_api_key = weather_key
        
        st.markdown("---")
        
        # Location section
        st.markdown("### 📍 Location")
        
        city = st.text_input(
            "City",
            value=st.session_state.get("city", "New York"),
            help="Enter city name"
        )
        st.session_state.city = city
        
        st.markdown("---")
        
        # Demo mode toggle
        demo_mode = st.toggle(
            "🎮 Demo Mode",
            value=st.session_state.get("demo_mode", True),
            help="Use demo data (no API keys needed)"
        )
        st.session_state.demo_mode = demo_mode
        
        if demo_mode:
            st.info("Demo mode enabled. Using simulated data.")
        
        st.markdown("---")
        
        # Info section
        st.markdown("""
        <div style="padding: 1rem; background: rgba(99, 102, 241, 0.1); border-radius: 12px; margin-top: 1rem;">
            <h4 style="color: white; margin: 0 0 0.5rem 0;">ℹ️ About</h4>
            <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem; margin: 0;">
                SkyCoach AI uses GPT-4 to understand your activities and real-time weather data to calculate the perfect "SkyScore" for your plans.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # History section
        st.markdown("---")
        st.markdown("### 📜 Recent History")
        
        history = st.session_state.get("history", [])
        if history:
            for entry in history[-5:][::-1]:  # Show last 5, newest first
                score_color = "#10b981" if entry.score >= 70 else "#f59e0b" if entry.score >= 40 else "#ef4444"
                st.markdown(f"""
                <div class="history-item">
                    <div>
                        <div style="color: white; font-weight: 500;">{entry.activity}</div>
                        <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{entry.timestamp}</div>
                    </div>
                    <div style="color: {score_color}; font-weight: 600;">{entry.score}%</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="color: rgba(255,255,255,0.4); font-size: 0.85rem; text-align: center; padding: 1rem;">
                No history yet. Analyze an activity to get started!
            </div>
            """, unsafe_allow_html=True)


def get_alternative_activities(classification: str, weather: WeatherData) -> list:
    """Suggest alternative activities based on weather and classification."""
    
    outdoor_activities = [
        ("🚶 Go for a walk", "Perfect for clear weather"),
        ("🚴 Cycling", "Great cardio in good conditions"),
        ("🌱 Gardening", "Connect with nature"),
        ("📸 Photography", "Capture beautiful moments"),
        ("🏃 Jogging", "Get your heart pumping"),
        ("🎣 Fishing", "Relaxing outdoor activity"),
    ]
    
    indoor_activities = [
        ("📚 Reading", "Expand your knowledge"),
        ("🎮 Gaming", "Entertainment indoors"),
        ("🧘 Yoga", "Mind and body wellness"),
        ("👨‍🍳 Cooking", "Try a new recipe"),
        ("🎨 Art & Crafts", "Express your creativity"),
        ("🎬 Movie marathon", "Cozy entertainment"),
    ]
    
    rainy_activities = [
        ("☕ Coffee & reading", "Perfect rainy day activity"),
        ("🎵 Listen to music", "Relaxing indoor time"),
        ("📝 Journaling", "Reflect and write"),
        ("🧩 Puzzles", "Challenge your mind"),
    ]
    
    hot_activities = [
        ("🏊 Swimming", "Cool off in the water"),
        ("🍦 Ice cream trip", "Beat the heat"),
        ("🛒 Mall visit", "AC and shopping"),
    ]
    
    suggestions = []
    
    if weather.is_raining:
        suggestions.extend(rainy_activities[:3])
    elif weather.temp_celsius > 30:
        suggestions.extend(hot_activities[:2])
        suggestions.extend(indoor_activities[:2])
    elif classification == "Outdoor" and weather.wind_mph > 15:
        suggestions.extend(indoor_activities[:3])
    elif classification == "Indoor" and not weather.is_raining and weather.temp_celsius < 28:
        suggestions.extend(outdoor_activities[:3])
    else:
        # Mix of both
        suggestions.extend(indoor_activities[:2])
        suggestions.extend(outdoor_activities[:2])
    
    return suggestions[:4]


def render_alternatives(classification: str, weather: WeatherData):
    """Render alternative activity suggestions."""
    alternatives = get_alternative_activities(classification, weather)
    
    if not alternatives:
        return
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">💡 Alternative Ideas</h3>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, (activity, description) in enumerate(alternatives):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="alt-activity">
                <div style="font-size: 1.2rem; margin-bottom: 0.25rem;">{activity}</div>
                <div style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">{description}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_mini_forecast(city: str, demo_mode: bool = True):
    """Render a mini weather forecast preview."""
    # In demo mode, generate fake forecast
    hours = ["Now", "+3h", "+6h", "+9h", "+12h"]
    
    # Generate consistent forecast based on city
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)
    
    conditions = [
        ("☀️", "Clear"),
        ("⛅", "Partly Cloudy"),
        ("☁️", "Cloudy"),
        ("🌧️", "Rain"),
    ]
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="color: white; margin-bottom: 1rem;">🕐 Upcoming Weather</h3>
        <div style="display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.5rem;">
    """, unsafe_allow_html=True)
    
    forecast_html = '<div style="display: flex; gap: 0.75rem; justify-content: space-between;">'
    
    for i, hour in enumerate(hours):
        idx = (city_hash + i) % len(conditions)
        emoji, _ = conditions[idx]
        temp = 20 + ((city_hash + i * 3) % 15)
        
        forecast_html += f'''
        <div class="forecast-item">
            <div style="color: rgba(255,255,255,0.5); font-size: 0.75rem;">{hour}</div>
            <div style="font-size: 1.5rem; margin: 0.25rem 0;">{emoji}</div>
            <div style="color: white; font-weight: 500;">{temp}°</div>
        </div>
        '''
    
    forecast_html += '</div>'
    
    st.markdown(forecast_html + "</div></div>", unsafe_allow_html=True)


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    """Main Streamlit application."""
    
    # Page config
    st.set_page_config(
        page_title="SkyCoach AI",
        page_icon="🌤️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject custom styles
    inject_custom_css()
    inject_gsap_animations()
    
    # Initialize session state
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    if "demo_mode" not in st.session_state:
        st.session_state.demo_mode = True
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_hero()
    
    # Input section
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div class="glass-card">
            <h3 style="color: white; margin-bottom: 1rem;">💭 What do you want to do?</h3>
        """, unsafe_allow_html=True)
        
        user_input = st.text_area(
            "Activity",
            placeholder="e.g., 'washin my car' or 'gonna do sum gardning today'",
            height=100,
            label_visibility="collapsed"
        )
        
        analyze_btn = st.button("🚀 Analyze Activity", use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Process and display results
    if analyze_btn and user_input:
        with st.spinner("🔮 Analyzing your activity..."):
            config = Config()
            
            # Step 1: Analyze task
            demo_mode = st.session_state.get("demo_mode", True)
            openai_key = st.session_state.get("openai_api_key", "")
            weather_key = st.session_state.get("openweather_api_key", "")
            city = st.session_state.get("city", "New York")
            
            if demo_mode or not openai_key:
                task = analyze_task_fallback(user_input)
            else:
                try:
                    task = analyze_task_openai(user_input, openai_key)
                except Exception as e:
                    st.warning(f"OpenAI error, using fallback: {str(e)[:50]}")
                    task = analyze_task_fallback(user_input)
            
            time.sleep(0.5)  # Brief pause for effect
            
            # Step 2: Get weather
            if demo_mode or not weather_key:
                weather = get_demo_weather(city)
            else:
                try:
                    weather = get_weather_by_city(city, weather_key)
                except Exception as e:
                    st.warning(f"Weather API error, using demo: {str(e)[:50]}")
                    weather = get_demo_weather(city)
            
            time.sleep(0.3)
            
            # Step 3: Calculate score
            result = calculate_sky_score(task, weather, config)
            
            # Step 4: Save to history
            if "history" not in st.session_state:
                st.session_state.history = []
            
            history_entry = HistoryEntry(
                timestamp=datetime.now().strftime("%H:%M"),
                activity=task.activity[:20],
                classification=task.classification,
                score=result.score,
                city=weather.city,
                weather_condition=weather.condition
            )
            st.session_state.history.append(history_entry)
            
            # Keep only last 10 entries
            if len(st.session_state.history) > 10:
                st.session_state.history = st.session_state.history[-10:]
            
            # Store in session state
            st.session_state.task = task
            st.session_state.weather = weather
            st.session_state.result = result
            st.session_state.analyzed = True
    
    # Display results if we have them
    if st.session_state.get("analyzed"):
        task = st.session_state.task
        weather = st.session_state.weather
        result = st.session_state.result
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Results layout
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Score gauge
            render_score_gauge(result.score, result.classification)
            
            # Weather card
            render_weather_card(weather)
        
        with col2:
            # Analysis card
            render_analysis_card(task)
            
            # Factors card
            render_factors_card(result)
        
        # Map section
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Two column layout for map and forecast
        map_col, forecast_col = st.columns([2, 1])
        
        with map_col:
            st.markdown("""
            <div class="glass-card">
                <h3 style="color: white; margin-bottom: 1rem;">🗺️ Weather Map</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Render map
            weather_map = render_map(weather.latitude, weather.longitude, weather.city, weather)
            st_folium(weather_map, width=None, height=350, use_container_width=True)
        
        with forecast_col:
            # Mini forecast
            city = st.session_state.get("city", "New York")
            render_mini_forecast(city, st.session_state.get("demo_mode", True))
            
            # Alternative activities
            st.markdown("<br>", unsafe_allow_html=True)
            render_alternatives(result.classification, weather)


if __name__ == "__main__":
    main()
