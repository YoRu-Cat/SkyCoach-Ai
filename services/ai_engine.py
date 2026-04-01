import hashlib
import requests
import json
from typing import Optional
from models.data_classes import WeatherData, TaskAnalysis, Config


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
    """Demo weather data for testing without API."""
    city_hash = int(hashlib.md5(city.lower().encode()).hexdigest()[:8], 16)
    
    scenarios = [
        ("Clear", "clear sky", "01d", False, 0.0, 26.0),
        ("Clouds", "scattered clouds", "03d", False, 0.0, 22.0),
        ("Rain", "light rain", "10d", True, 2.5, 18.0),
        ("Clouds", "overcast clouds", "04d", False, 0.0, 20.0),
        ("Clear", "sunny", "01d", False, 0.0, 32.0),
    ]
    
    scenario_idx = city_hash % len(scenarios)
    condition, desc, icon, is_rain, rain_amt, base_temp = scenarios[scenario_idx]
    
    temp_var = (city_hash % 10) - 5
    wind_base = 3 + (city_hash % 15)
    humidity = 40 + (city_hash % 40)
    
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
