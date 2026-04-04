import re
from difflib import SequenceMatcher, get_close_matches
from typing import Optional, Tuple

ACTIVITY_CORPUS = {
    "Outdoor": [
        "playing soccer", "playing football", "soccer", "football",
        "running", "jogging", "sprint",
        "cycling", "biking", "bike riding",
        "hiking", "trekking", "trail walking",
        "swimming", "swimming pool",
        "playing tennis", "tennis",
        "basketball", "playing basketball",
        "baseball", "playing baseball",
        "volleyball", "playing volleyball",
        "skiing", "snowboarding",
        "rock climbing", "climbing",
        "skateboarding", "skating",
        "surfing", "windsurfing",
        "kayaking", "canoeing",
        "fishing",
        "golfing", "golf",
        "playing catch", "catch",
        "outdoor games", "outdoor sports",
        "yard work", "yardwork",
        "gardening", "garden",
        "mowing lawn", "mow lawn", "lawn mowing",
        "raking leaves", "rake leaves",
        "hedge trimming", "trim hedge",
        "dog walking", "walk dog",
        "pet walking", "walk pet",
        "picnic",
        "camping", "camp",
        "outdoor cooking", "bbq", "barbecue",
        "bird watching", "birdwatching",
        "nature walk", "nature hike",
        "photography", "photo walk",
        "washing car", "wash car", "car washing",
        "car wash",
        "going to gym outside", "outdoor workout", "outdoor training",
    ],
    "Indoor": [
        "wedding ceremony", "wedding", "attending wedding",
        "birthday party", "anniversary celebration", "family gathering",
        "office meeting", "business meeting", "conference", "seminar", "classroom session",
        "doing homework", "homework",
        "studying", "study", "studying for exam",
        "working", "work", "office work",
        "coding", "programming", "writing code",
        "reading", "reading book",
        "watching movie", "movie", "watch movie",
        "playing video game", "video game", "gaming",
        "cooking", "cook", "cooking meal", "meal prep",
        "baking", "bake", "baking cake",
        "drawing", "sketching", "art",
        "painting", "paint",
        "writing", "write", "writing essay",
        "music", "playing music", "playing instrument",
        "dancing", "dance",
        "yoga", "doing yoga",
        "exercise", "workout", "exercising",
        "meditation", "meditating",
        "stretching", "stretch",
        "board game", "playing board game",
        "puzzle", "doing puzzle",
        "crafting", "craft", "diy",
        "knitting", "sewing", "quilting",
        "building", "building lego", "model building",
        "cleaning", "clean house", "house cleaning",
        "laundry", "doing laundry",
        "ironing", "iron clothes",
        "organizing", "organize room",
        "shopping", "grocery shopping",
        "listening music", "listen music",
        "podcast", "listen podcast",
        "audiobook", "listening audiobook",
        "socializing", "hang out", "hanging out",
        "gaming", "online gaming",
        "streaming", "watch stream",
        "blogging", "writing blog",
        "photo editing", "edit photo",
        "video editing", "edit video",
        "going to gym", "gym workout", "indoor workout",
    ]
}

ALL_ACTIVITIES = [
    activity for activities in ACTIVITY_CORPUS.values() for activity in activities
]


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-z]+\b", _normalize(text)))


def _phrase_variants(label: str, phrase: str) -> list[str]:
    base = _normalize(phrase)
    if not base:
        return []

    variants = {
        base,
        _normalize(f"going to {base}"),
        _normalize(f"doing {base}"),
        _normalize(f"planning {base}"),
    }

    if label == "Outdoor":
        variants.add(_normalize(f"outside {base}"))
        variants.add(_normalize(f"{base} outside"))
        variants.add(_normalize(f"going outside for {base}"))
    else:
        variants.add(_normalize(f"inside {base}"))
        variants.add(_normalize(f"{base} indoors"))
        variants.add(_normalize(f"at home {base}"))

    return [variant for variant in variants if variant]


def classify_with_dictionary(activity_text: str) -> tuple[str, float, Optional[str]]:
    """Classify activity as Indoor/Outdoor by matching against imported ACTIVITY_CORPUS."""
    normalized_input = _normalize(activity_text)
    if not normalized_input:
        return "Indoor", 0.0, None

    input_tokens = _tokenize(normalized_input)
    best_label = "Indoor"
    best_phrase: Optional[str] = None
    best_score = 0.0

    for label, activities in ACTIVITY_CORPUS.items():
        for phrase in activities:
            for variant in _phrase_variants(label, phrase):
                phrase_tokens = _tokenize(variant)
                token_overlap = 0.0
                if input_tokens and phrase_tokens:
                    token_overlap = len(input_tokens & phrase_tokens) / len(input_tokens | phrase_tokens)

                char_similarity = calculate_similarity(normalized_input, variant)
                starts_with_bonus = 0.08 if normalized_input.startswith(variant) or variant.startswith(normalized_input) else 0.0

                environment_bonus = 0.0
                if ("outside" in input_tokens or "outdoor" in input_tokens) and label == "Outdoor":
                    environment_bonus += 0.14
                if ("inside" in input_tokens or "indoor" in input_tokens or "home" in input_tokens) and label == "Indoor":
                    environment_bonus += 0.14

                score = token_overlap * 0.58 + char_similarity * 0.34 + starts_with_bonus + environment_bonus

                if score > best_score:
                    best_score = score
                    best_label = label
                    best_phrase = phrase

    return best_label, min(best_score, 0.99), best_phrase


def calculate_similarity(input_str: str, candidate: str) -> float:
    return SequenceMatcher(None, input_str.lower(), candidate.lower()).ratio()


def extract_words(text: str) -> list[str]:
    return re.findall(r'\b[a-z]+\b', text.lower())


def suggest_activity(broken_input: str) -> Optional[Tuple[str, float, str]]:
    if not broken_input or len(broken_input.strip()) < 3:
        return None
    
    cleaned = broken_input.strip().lower()
    
    close_matches = get_close_matches(cleaned, ALL_ACTIVITIES, n=5, cutoff=0.4)
    
    best_match = None
    best_score = 0
    
    if not close_matches:
        words = extract_words(broken_input)
        
        for activity in ALL_ACTIVITIES:
            activity_words = set(extract_words(activity))
            input_words = set(words)
            
            if not input_words or not activity_words:
                continue
            
            intersection = len(input_words & activity_words)
            if intersection == 0:
                continue
            
            overlap_ratio = intersection / max(len(input_words), len(activity_words))
            char_similarity = calculate_similarity(cleaned, activity)
            
            similarity = overlap_ratio * 0.65 + char_similarity * 0.35
            
            if similarity > best_score:
                best_score = similarity
                best_match = activity
        
        if best_match and best_score > 0.4:
            suggestion = best_match
            confidence = best_score
        else:
            return None
    else:
        suggestion = close_matches[0]
        confidence = calculate_similarity(cleaned, suggestion)
    
    classification = None
    for cat, activities in ACTIVITY_CORPUS.items():
        if suggestion in activities:
            classification = cat
            break
    
    if not classification:
        classification = "Indoor"
    
    return (suggestion, confidence, classification)


def auto_judge_input(text: str) -> dict:
    suggestion_result = suggest_activity(text)
    
    if suggestion_result:
        suggestion, confidence, classification = suggestion_result
        return {
            "original": text,
            "is_broken": True,
            "suggestion": suggestion,
            "confidence": confidence,
            "classification": classification,
        }
    
    return {
        "original": text,
        "is_broken": False,
        "suggestion": None,
        "confidence": 0.0,
        "classification": None,
    }


if __name__ == "__main__":
    test_cases = [
        "doing homewo",
        "wash car",
        "play socc",
        "biking",
        "read book",
        "cooking diner",
        "exerciz",
    ]
    
    for test in test_cases:
        result = auto_judge_input(test)
        print(f"Input: '{test}'")
        print(f"  Broken: {result['is_broken']}")
        if result['suggestion']:
            print(f"  Suggestion: {result['suggestion']}")
            print(f"  Confidence: {result['confidence']:.2f}")
            print(f"  Classification: {result['classification']}")
        print()
