from typing import List, Tuple
from models.data_classes import TaskAnalysis, WeatherData, SkyScoreResult, Config


def calculate_sky_score(task: TaskAnalysis, weather: WeatherData, config: Config) -> SkyScoreResult:
    if getattr(task, "needs_clarification", False) or task.confidence < 0.25:
        return SkyScoreResult(
            score=0,
            classification=task.classification,
            weather_factors=["⚠️ Activity input needs clarification"],
            bonuses=[],
            penalties=[],
            recommendation=task.issue or "Please enter a complete activity description so I can analyze it accurately.",
        )

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
    
    # Neutral factors
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


def get_alternative_activities(classification: str, weather: WeatherData) -> List[Tuple[str, str]]:
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
        suggestions.extend(indoor_activities[:2])
        suggestions.extend(outdoor_activities[:2])
    
    return suggestions[:4]
