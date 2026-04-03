import hashlib
import os
import re
import requests
import json
from typing import Optional
from models.data_classes import WeatherData, TaskAnalysis, Config
from services.auto_judge import auto_judge_input


RULE_JUDGE_MODEL_NAME = "SkyCoach RuleJudge v1"


def _stable_fallback_coords(city: str) -> tuple[float, float]:
    digest = hashlib.md5(city.lower().encode()).hexdigest()
    lat_bucket = int(digest[:6], 16) / 0xFFFFFF
    lon_bucket = int(digest[6:12], 16) / 0xFFFFFF
    lat = (lat_bucket * 120.0) - 60.0
    lon = (lon_bucket * 300.0) - 150.0
    return (round(lat, 4), round(lon, 4))


def _resolve_demo_city_coords(city: str, city_coords: dict) -> tuple[float, float]:
    normalized = city.lower().strip()
    if normalized in city_coords:
        return city_coords[normalized]

    try:
        from geopy.geocoders import Nominatim

        geolocator = Nominatim(user_agent="skycoach_demo_locator", timeout=3)
        location = geolocator.geocode(city)
        if location is not None:
            return (round(location.latitude, 4), round(location.longitude, 4))
    except Exception:
        pass

    return _stable_fallback_coords(city)


def _count_keyword_matches(text: str, keywords: list[str]) -> int:
    count = 0
    for keyword in keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            count += 1
    return count


def _score_keyword_matches(text: str, weighted_keywords: list[tuple[str, float]]) -> tuple[float, list[str]]:
    score = 0.0
    matches: list[str] = []
    for keyword, weight in weighted_keywords:
        pattern = r"\b" + re.escape(keyword) + r"\b"
        if re.search(pattern, text):
            score += weight
            matches.append(keyword)
    return score, matches


def _detect_input_issue(text: str, outdoor_score: int, indoor_score: int) -> tuple[bool, Optional[str]]:
    compact = re.sub(r"\s+", " ", text).strip()
    words = re.findall(r"[a-zA-Z']+", compact.lower())
    filler_words = {
        "doing", "go", "going", "make", "want", "need", "plan", "try",
        "do", "to", "a", "an", "the", "some", "something", "thing",
    }

    if len(compact) < 8 or len(words) < 2:
        return True, "Input is too short or incomplete"

    if outdoor_score == 0 and indoor_score == 0:
        content_words = [w for w in words if w not in filler_words and len(w) >= 3]
        # A single concrete content word can still be a valid intent phrase,
        # e.g. "going to gym" or "going to work".
        if len(content_words) >= 1:
            return False, None
        if any(word in filler_words for word in words):
            return True, "Input looks unfinished or misspelled"
        return True, "Could not identify a clear activity"

    return False, None


def _has_word_overlap(input_text: str, suggestion_text: str) -> bool:
    input_words = set(re.findall(r"[a-zA-Z']+", input_text.lower()))
    suggestion_words = set(re.findall(r"[a-zA-Z']+", suggestion_text.lower()))
    return len(input_words & suggestion_words) > 0


def _apply_auto_judge_resolution(
    original_text: str,
    needs_clarification: bool,
    issue_text: Optional[str],
    activity: str,
    classification: str,
    confidence: float,
    reasoning: str,
) -> tuple[bool, Optional[str], str, str, float, str, Optional[str], Optional[str], float]:
    suggested_activity = None
    suggested_classification = None
    suggestion_confidence = 0.0

    if not needs_clarification:
        return (
            needs_clarification,
            issue_text,
            activity,
            classification,
            confidence,
            reasoning,
            suggested_activity,
            suggested_classification,
            suggestion_confidence,
        )

    judge_result = auto_judge_input(original_text)
    if judge_result["is_broken"] and judge_result["suggestion"]:
        suggested_activity = judge_result["suggestion"]
        suggested_classification = judge_result["classification"]
        suggestion_confidence = judge_result["confidence"]

        if suggestion_confidence >= 0.78 and _has_word_overlap(original_text, suggested_activity):
            activity = suggested_activity
            classification = suggested_classification or classification
            confidence = max(confidence, min(0.94, suggestion_confidence))
            needs_clarification = False
            issue_text = None
            reasoning = "Auto-corrected with high-confidence suggestion"

    return (
        needs_clarification,
        issue_text,
        activity,
        classification,
        confidence,
        reasoning,
        suggested_activity,
        suggested_classification,
        suggestion_confidence,
    )


def analyze_task_openai(text: str, api_key: str, model: str = "gpt-4o-mini") -> TaskAnalysis:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    system_prompt = """You are SkyCoach's Task Analysis Engine.

Return ONLY JSON with this exact shape:
{
  "cleaned_text": "Corrected text",
  "activity": "Core activity (2-4 words)",
  "classification": "Indoor" or "Outdoor",
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation"
}

Classification policy (strict):
- Use only "Indoor" or "Outdoor".
- Physical training activities are Outdoor by default: gym, workout, exercise, training, fitness, cardio, lifting.
- Indoor examples: cooking, reading, coding, office work, studying, cleaning indoors, gaming.
- Outdoor examples: running, jogging, cycling, hiking, field sports, gardening, car washing.
- If wording is ambiguous, choose the most likely real-world interpretation and lower confidence.

Examples:
- "going to gym" -> classification: "Outdoor"
- "doing workout" -> classification: "Outdoor"
- "studying for exam" -> classification: "Indoor"
"""


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
    original_text = text.strip()
    cleaned_text = result.get("cleaned_text", text)
    issue_text = result.get("issue")
    needs_clarification = bool(result.get("needs_clarification", False))

    outdoor_keywords = ["wash car", "washing car", "car wash", "car washing", "garden", "gardening", "jog", "jogging", "run", "running", "hike", "hiking", "bike", "biking", "cycle", "cycling", "walk", "walking", "dog walk", "dog walking", "picnic", "bbq", "swim", "swimming", "yard work", "lawn", "mow lawn", "paint outside", "sports", "sport", "soccer", "football", "cricket", "baseball", "basketball", "volleyball", "tennis", "golf", "park", "outside"]
    indoor_keywords = ["cook", "cooking", "read", "reading", "clean", "cleaning", "computer", "work", "working", "study", "studying", "watch", "watching", "game", "gaming", "craft", "crafts", "laundry", "yoga", "inside", "homework", "at home", "wedding", "ceremony", "event", "meeting", "conference", "class", "seminar"]
    outdoor_score = _count_keyword_matches(original_text.lower(), outdoor_keywords)
    indoor_score = _count_keyword_matches(original_text.lower(), indoor_keywords)
    detected_issue, detected_issue_text = _detect_input_issue(original_text, outdoor_score, indoor_score)

    activity = result.get("activity", "Needs clarification") if not needs_clarification else "Needs clarification"
    classification = result.get("classification", "Indoor")
    confidence = 0.15 if needs_clarification else float(result.get("confidence", 0.8))
    reasoning = (result.get("reasoning", "") + (f". {issue_text}" if issue_text else "")).strip()

    if detected_issue:
        needs_clarification = True
        issue_text = detected_issue_text

    (
        needs_clarification,
        issue_text,
        activity,
        classification,
        confidence,
        reasoning,
        suggested_activity,
        suggested_classification,
        suggestion_confidence,
    ) = _apply_auto_judge_resolution(
        original_text=original_text,
        needs_clarification=needs_clarification,
        issue_text=issue_text,
        activity=activity,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
    )
    
    return TaskAnalysis(
        original_text=text,
        cleaned_text=cleaned_text,
        activity=activity,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
        needs_clarification=needs_clarification,
        issue=issue_text,
        suggested_activity=suggested_activity,
        suggested_classification=suggested_classification,
        suggestion_confidence=suggestion_confidence,
    )


def analyze_task_fallback(text: str) -> TaskAnalysis:
    text_lower = re.sub(r"\s+", " ", text.lower().strip())

    outdoor_weighted = [
        ("going to work outside", 5.0), ("work outside", 4.5), ("outside work", 4.2),
        ("going to gym", 4.5), ("gym", 4.0), ("workout", 4.0), ("exercise", 3.8),
        ("training", 3.6), ("fitness", 3.4), ("cardio", 3.2), ("lifting", 3.2),
        ("weight training", 3.6), ("run", 3.0), ("running", 3.0), ("jog", 3.0),
        ("jogging", 3.0), ("walk", 2.4), ("walking", 2.4), ("cycling", 3.0),
        ("cycle", 3.0), ("hiking", 3.0), ("hike", 3.0), ("soccer", 3.2),
        ("cricket", 3.2), ("football", 3.2), ("tennis", 2.8), ("basketball", 3.0),
        ("swimming", 2.8), ("garden", 2.7), ("gardening", 2.7), ("wash car", 2.8),
        ("car wash", 2.8), ("outside", 2.2), ("park", 2.0),
    ]
    indoor_weighted = [
        ("going to work", 2.8), ("work", 1.0), ("office", 2.8), ("desk", 2.2),
        ("study", 2.8), ("studying", 2.8), ("homework", 3.0), ("read", 2.4),
        ("reading", 2.4), ("coding", 2.6), ("meeting", 2.6), ("conference", 2.6),
        ("class", 2.4), ("cook", 2.5), ("cooking", 2.5), ("clean", 2.3),
        ("cleaning", 2.3), ("dishes", 2.5), ("laundry", 2.4), ("gaming", 2.3),
        ("movie", 2.0), ("inside", 2.2), ("at home", 2.0),
    ]

    outdoor_score, outdoor_matches = _score_keyword_matches(text_lower, outdoor_weighted)
    indoor_score, indoor_matches = _score_keyword_matches(text_lower, indoor_weighted)
    needs_clarification, issue = _detect_input_issue(text, outdoor_score, indoor_score)

    if needs_clarification:
        classification = "Indoor"
        confidence = 0.20
        activity = "Needs clarification"
        reasoning = issue or f"{RULE_JUDGE_MODEL_NAME}: Input is incomplete or unclear"
    elif outdoor_score > indoor_score:
        classification = "Outdoor"
        margin = outdoor_score - indoor_score
        total = max(outdoor_score + indoor_score, 1.0)
        confidence = min(0.96, 0.60 + (margin / total) * 0.25 + min(outdoor_score, 8.0) * 0.02)
        activity = text[:30]
        reasoning = f"{RULE_JUDGE_MODEL_NAME}: outdoor score {outdoor_score:.1f} > indoor {indoor_score:.1f}; matched {', '.join(outdoor_matches[:3]) or 'context cues'}"
    else:
        classification = "Indoor"
        margin = indoor_score - outdoor_score
        total = max(outdoor_score + indoor_score, 1.0)
        confidence = min(0.96, 0.60 + (margin / total) * 0.25 + min(indoor_score, 8.0) * 0.02)
        activity = text[:30]
        reasoning = f"{RULE_JUDGE_MODEL_NAME}: indoor score {indoor_score:.1f} >= outdoor {outdoor_score:.1f}; matched {', '.join(indoor_matches[:3]) or 'context cues'}"

    (
        needs_clarification,
        issue,
        activity,
        classification,
        confidence,
        reasoning,
        suggested_activity,
        suggested_classification,
        suggestion_confidence,
    ) = _apply_auto_judge_resolution(
        original_text=text,
        needs_clarification=needs_clarification,
        issue_text=issue,
        activity=activity,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
    )
    
    return TaskAnalysis(
        original_text=text,
        cleaned_text=text.title(),
        activity=activity,
        classification=classification,
        confidence=confidence,
        reasoning=reasoning,
        needs_clarification=needs_clarification,
        issue=issue,
        suggested_activity=suggested_activity,
        suggested_classification=suggested_classification,
        suggestion_confidence=suggestion_confidence,
    )


def analyze_task_smart(
    text: str,
    use_openai: bool = False,
    openai_api_key: Optional[str] = None,
    model: str = "gpt-4o-mini",
    min_confidence_for_openai: float = 0.70,
) -> TaskAnalysis:
    """Use OpenAI directly when requested, otherwise use local keyword analysis."""
    if use_openai:
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OpenAI API key is required when use_openai=True")

        return analyze_task_openai(text, api_key=api_key, model=model)

    return analyze_task_fallback(text)


def get_weather(lat: float, lon: float, api_key: str, units: str = "metric") -> WeatherData:
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


def get_demo_weather(
    city: str = "New York",
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> WeatherData:
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
        "lahore": (31.5204, 74.3587),
        "karachi": (24.8607, 67.0011),
        "islamabad": (33.6844, 73.0479),
        "delhi": (28.6139, 77.2090),
        "beijing": (39.9042, 116.4074),
        "berlin": (52.5200, 13.4050),
    }

    if latitude is not None and longitude is not None:
        lat, lon = latitude, longitude
    else:
        lat, lon = _resolve_demo_city_coords(city, city_coords)
    
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
