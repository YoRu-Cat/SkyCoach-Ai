from typing import List, Tuple, Optional
from datetime import datetime, timedelta
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


def _score_slot_for_task(task: TaskAnalysis, slot: dict) -> tuple[float, str]:
    is_outdoor = task.classification == "Outdoor"
    confidence = float(getattr(task, "confidence", 0.0) or 0.0)

    temp_c = float(slot.get("temp_c", 24.0))
    wind_mph = float(slot.get("wind_mph", 5.0))
    rain_1h = float(slot.get("rain_1h", 0.0))
    is_raining = bool(slot.get("is_raining", False))

    score = 100.0
    reasons: list[str] = []

    if is_outdoor:
        if is_raining or rain_1h > 0.2:
            score -= 45
            reasons.append("rain risk")
        if wind_mph > 18:
            score -= 18
            reasons.append("strong wind")
        if temp_c >= 34:
            score -= 22
            reasons.append("high heat")
        elif temp_c <= 7:
            score -= 12
            reasons.append("cold conditions")
        else:
            reasons.append("comfortable outdoor conditions")
    else:
        # Indoor tasks tolerate weather, but bad outdoor weather can be a positive.
        if is_raining or rain_1h > 0.2:
            score += 8
            reasons.append("rain favors indoor focus")
        if temp_c >= 33:
            score += 6
            reasons.append("heat favors indoor timing")
        if confidence < 0.65:
            score -= 8
            reasons.append("intent ambiguity, keep slot flexible")
        if not reasons:
            reasons.append("stable indoor slot")

    score = max(0.0, min(100.0, score))
    return score, ", ".join(reasons)


def recommend_best_schedule(
    task: TaskAnalysis,
    weather: WeatherData,
    forecast_slots: Optional[list[dict]] = None,
) -> tuple[str, str, str]:
    """Recommend best date/time slot for a task from current weather context.

    Heuristic-based recommendation designed to avoid overly strict blocking while
    still respecting key weather constraints for indoor/outdoor activities.
    """
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    temp_c = weather.temp_celsius if hasattr(weather, "temp_celsius") else weather.temperature
    is_outdoor = task.classification == "Outdoor"
    confidence = float(getattr(task, "confidence", 0.0) or 0.0)

    if forecast_slots:
        best = None
        best_score = -1.0
        best_reason = ""
        for slot in forecast_slots:
            score, reason = _score_slot_for_task(task, slot)
            if score > best_score:
                best = slot
                best_score = score
                best_reason = reason

        if best is not None:
            return (
                str(best.get("date", today.isoformat())),
                str(best.get("time_range", "09:00-11:00")),
                f"Best slot selected from multi-day forecast ({best_reason}).",
            )

    if is_outdoor:
        if weather.is_raining or weather.rain_1h > 0.2:
            return (
                tomorrow.isoformat(),
                "08:00-10:00",
                "Rain is active now; next morning is safer for outdoor plans.",
            )
        if weather.wind_mph > 18:
            return (
                today.isoformat(),
                "16:30-18:30",
                "Wind is currently strong; later daylight hours are likely more comfortable.",
            )
        if temp_c >= 33:
            return (
                today.isoformat(),
                "06:30-08:30",
                "Heat is high; early morning minimizes thermal stress outdoors.",
            )
        if temp_c <= 8:
            return (
                today.isoformat(),
                "11:00-13:00",
                "Cool conditions favor a late-morning outdoor slot.",
            )
        return (
            today.isoformat(),
            "07:30-09:30",
            "Current weather is suitable for an outdoor session this morning.",
        )

    # Indoor: allow flexibility, but leverage bad weather/high heat as strong positives.
    if weather.is_raining or weather.rain_1h > 0.2:
        return (
            today.isoformat(),
            "18:00-20:00",
            "Rainy weather pairs well with indoor tasks in the evening.",
        )
    if temp_c >= 33:
        return (
            today.isoformat(),
            "13:00-15:00",
            "Peak heat hours are optimal for staying indoors.",
        )
    if confidence < 0.65:
        return (
            today.isoformat(),
            "17:00-18:00",
            "Task intent is somewhat ambiguous; a flexible early-evening slot is recommended.",
        )
    return (
        today.isoformat(),
        "10:00-12:00",
        "Stable conditions and indoor classification support a productive mid-morning slot.",
    )
