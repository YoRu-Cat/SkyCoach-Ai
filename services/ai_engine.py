import hashlib
import os
import re
import requests
import json
from typing import Optional
from models.data_classes import WeatherData, TaskAnalysis, Config
from services.auto_judge import auto_judge_input, classify_with_dictionary
from services.task_classifier_ml import predict_task_label


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


def _detect_input_issue(text: str, outdoor_score: float, indoor_score: float) -> tuple[bool, Optional[str]]:
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


def _openai_json_response(client, model: str, system_prompt: str, user_prompt: str) -> dict:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        max_tokens=180,
        temperature=0.2,
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)


def _verify_openai_classification(
    client,
    model: str,
    original_text: str,
    cleaned_text: str,
    rephrased_activity: str,
    local_activity: str,
    local_classification: str,
    local_confidence: float,
    local_reasoning: str,
    suggested_activity: Optional[str],
    suggested_classification: Optional[str],
    suggestion_confidence: float,
) -> dict:
    system_prompt = """You verify an activity classification after a local judge has already made a decision.
Return ONLY JSON with these keys:
{
  "classification": "Indoor" or "Outdoor",
  "confidence": 0.0,
  "reasoning": "short explanation",
  "corrected_activity": "optional corrected activity text"
}
Use the original text, the rephrased text, and the local judgment. If the local judgment is correct, confirm it. If it is wrong, correct it. Prefer the user's intent over keyword traps.
"""

    user_prompt = json.dumps(
        {
            "original_text": original_text,
            "cleaned_text": cleaned_text,
            "rephrased_activity": rephrased_activity,
            "local_judgment": {
                "activity": local_activity,
                "classification": local_classification,
                "confidence": local_confidence,
                "reasoning": local_reasoning,
            },
            "auto_judge_suggestion": {
                "activity": suggested_activity,
                "classification": suggested_classification,
                "confidence": suggestion_confidence,
            },
        }
    )

    return _openai_json_response(client, model, system_prompt, user_prompt)


def analyze_task_openai(text: str, api_key: str, model: str = "gpt-4o-mini") -> TaskAnalysis:
    from openai import OpenAI
    
    client = OpenAI(api_key=api_key)
    
    rephrase_prompt = """You normalize user activities.
Return ONLY JSON:
{
  "cleaned_text": "Corrected natural text",
  "activity": "Core activity in 2-4 words"
}
Keep intent unchanged. Do not classify."""

    rephrased = _openai_json_response(
        client,
        model,
        rephrase_prompt,
        f"Rephrase activity: {text}",
    )

    original_text = text.strip()
    cleaned_text = rephrased.get("cleaned_text", text)
    activity = rephrased.get("activity", cleaned_text)

    issue_text = None
    needs_clarification = False

    classification, confidence, matched_phrase = classify_with_dictionary(
        activity,
        use_web_enrichment=False,
    )
    if confidence < 0.62:
        enriched_classification, enriched_confidence, enriched_match = classify_with_dictionary(
            activity,
            use_web_enrichment=True,
        )
        if enriched_confidence > confidence:
            classification, confidence, matched_phrase = (
                enriched_classification,
                enriched_confidence,
                enriched_match,
            )

    if confidence < 0.42:
        fallback_classification, fallback_confidence, fallback_match = classify_with_dictionary(
            cleaned_text,
            use_web_enrichment=False,
        )
        if fallback_confidence > confidence:
            classification, confidence, matched_phrase = (
                fallback_classification,
                fallback_confidence,
                fallback_match,
            )
        if confidence < 0.42:
            enriched_fallback_classification, enriched_fallback_confidence, enriched_fallback_match = classify_with_dictionary(
                cleaned_text,
                use_web_enrichment=True,
            )
            if enriched_fallback_confidence > confidence:
                classification, confidence, matched_phrase = (
                    enriched_fallback_classification,
                    enriched_fallback_confidence,
                    enriched_fallback_match,
                )

    if confidence < 0.42:
        needs_clarification = True
        issue_text = "Could not confidently map activity to the indoor/outdoor dictionary"

    match_text = matched_phrase or "closest dictionary phrase"
    reasoning = f"OpenAI rephrased activity, then web-enriched dictionary matched '{match_text}'"

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

    verification = _verify_openai_classification(
        client=client,
        model=model,
        original_text=original_text,
        cleaned_text=cleaned_text,
        rephrased_activity=activity,
        local_activity=activity,
        local_classification=classification,
        local_confidence=confidence,
        local_reasoning=reasoning,
        suggested_activity=suggested_activity,
        suggested_classification=suggested_classification,
        suggestion_confidence=suggestion_confidence,
    )

    verified_classification = verification.get("classification")
    if verified_classification not in {"Indoor", "Outdoor"}:
        verified_classification = classification

    verified_confidence = float(verification.get("confidence", 0.0) or 0.0)
    verified_reasoning = str(verification.get("reasoning", "OpenAI verification completed"))
    verified_activity = str(verification.get("corrected_activity") or activity)

    if verified_classification != classification:
        if verified_confidence >= max(0.72, confidence - 0.05):
            classification = verified_classification
            confidence = max(confidence, min(0.99, verified_confidence))
            activity = verified_activity
            reasoning = f"{reasoning}; OpenAI verification corrected the label to {classification.lower()} ({verified_reasoning})"
        else:
            reasoning = f"{reasoning}; OpenAI verification disagreed but was not stronger than the local judgment ({verified_reasoning})"
    else:
        confidence = max(confidence, min(0.99, (confidence + verified_confidence) / 2 if verified_confidence else confidence))
        activity = verified_activity
        reasoning = f"{reasoning}; OpenAI verification confirmed {classification.lower()} ({verified_reasoning})"
    
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
    compact_text = re.sub(r"\s+", " ", text.strip())
    activity = compact_text[:60]

    ml_label = None
    ml_confidence = 0.0
    ml_rationale = ""
    ml_suggestions: list[dict] = []

    # Primary runtime classifier: trained ML system model on disk.
    try:
        from ml_system.api import get_ml_system

        ml_result = get_ml_system().predict(text)
        ml_label = ml_result.get("label")
        ml_confidence = float(ml_result.get("confidence", 0.0) or 0.0)
        ml_rationale = str(ml_result.get("rationale", ""))
        ml_suggestions = ml_result.get("suggestions", []) or []
    except Exception:
        # Safety fallback for environments where unified model files are unavailable.
        legacy_prediction = predict_task_label(text)
        ml_label = legacy_prediction.classification
        ml_confidence = legacy_prediction.confidence
        ml_rationale = (
            f"{legacy_prediction.model_name} runtime fallback predicted "
            f"{legacy_prediction.classification.lower()} with {legacy_prediction.confidence:.2f} confidence"
        )

    dict_label, dict_confidence, dict_match = classify_with_dictionary(
        text,
        use_web_enrichment=False,
    )
    if dict_confidence < 0.62:
        enriched_label, enriched_confidence, enriched_match = classify_with_dictionary(
            text,
            use_web_enrichment=True,
        )
        if enriched_confidence > dict_confidence:
            dict_label, dict_confidence, dict_match = (
                enriched_label,
                enriched_confidence,
                enriched_match,
            )

    # Prefer calibrated ML output when confident; otherwise rely on dictionary evidence.
    if ml_label in {"Indoor", "Outdoor"}:
        classification = ml_label
        confidence = ml_confidence
    else:
        classification = dict_label if dict_confidence >= 0.52 else "Indoor"
        confidence = max(ml_confidence, dict_confidence * 0.9)

    disagreement_override = False
    if (
        ml_label in {"Indoor", "Outdoor"}
        and dict_confidence >= 0.8
        and dict_label != ml_label
        and ml_confidence < 0.75
    ):
        classification = dict_label
        confidence = min(0.88, max(dict_confidence * 0.85, ml_confidence))
        disagreement_override = True

    needs_clarification = False
    issue = None
    suggested_activity = None
    suggested_classification = None
    suggestion_confidence = 0.0

    if ml_suggestions:
        top = ml_suggestions[0]
        suggested_classification = top.get("label")
        suggestion_confidence = float(top.get("confidence", 0.0) or 0.0)

    if disagreement_override and not suggested_classification:
        suggested_classification = ml_label
        suggestion_confidence = ml_confidence

    # Clarify ambiguous intents instead of forcing hard labels on uncertain input.
    if ml_label == "Unclear" or max(ml_confidence, dict_confidence) < 0.62:
        needs_clarification = True
        issue = "Activity intent is understandable but ambiguous between indoor and outdoor"
        if dict_confidence >= 0.52:
            classification = dict_label
            confidence = min(0.7, max(dict_confidence, ml_confidence))

    suggestion = auto_judge_input(text)
    if suggestion["is_broken"] and suggestion["suggestion"]:
        suggested_activity = suggestion["suggestion"]
        if suggestion.get("classification"):
            suggested_classification = suggestion["classification"]
        suggestion_confidence = max(
            suggestion_confidence,
            float(suggestion.get("confidence", 0.0) or 0.0),
        )

        if suggestion_confidence >= 0.82 and _has_word_overlap(text, suggested_activity):
            activity = suggested_activity
            classification = suggested_classification or classification
            confidence = max(confidence, min(0.94, suggestion_confidence))
            needs_clarification = False
            issue = None

    reasoning_parts = []
    if ml_rationale:
        reasoning_parts.append(f"ML: {ml_rationale}")
    if dict_match and dict_confidence >= 0.52:
        reasoning_parts.append(f"Dictionary match: '{dict_match}' ({dict_confidence:.2f})")
    if disagreement_override:
        reasoning_parts.append("Dictionary override applied because semantic match strongly disagreed with low-confidence ML")
    if needs_clarification:
        reasoning_parts.append("Marked for clarification due to low or uncertain confidence")

    reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Local auto-judge analysis"

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
    """Task analysis always uses local Auto-Judge + ML runtime models."""
    _ = use_openai
    _ = openai_api_key
    _ = model
    _ = min_confidence_for_openai
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
