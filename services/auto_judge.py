import re
from functools import lru_cache
from difflib import SequenceMatcher, get_close_matches
import requests
from typing import Optional, Tuple

ACTIVITY_CORPUS = {
    "Outdoor": [
        "playing soccer", "playing football", "soccer", "football",
        "running", "jogging", "sprint",
        "cycling", "biking", "bike riding",
        "going to uni", "going to university", "going to college", "commuting to uni",
        "going to gym", "gym workout", "indoor workout",
        "amusement park", "amusement park date", "date at amusement park",
        "date in the park", "date outdoors", "date outside",
        "outdoor date", "romantic walk in the park",
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
        "shopping", "grocery shopping", "market shopping", "mall shopping",
    ],
    "Indoor": [
        "wedding ceremony", "wedding", "attending wedding",
        "birthday party", "anniversary celebration", "family gathering",
        "going on a date", "date night", "dinner date", "coffee date", "romantic date",
        "date at a restaurant", "date at a cafe", "movie date", "date night at home",
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
        "online shopping", "shop online",
        "listening music", "listen music",
        "podcast", "listen podcast",
        "audiobook", "listening audiobook",
        "socializing", "hang out", "hanging out",
        "gaming", "online gaming",
        "streaming", "watch stream",
        "blogging", "writing blog",
        "photo editing", "edit photo",
        "video editing", "edit video",
        "gooning", "goon",
    ]
}

ALL_ACTIVITIES = [
    activity for activities in ACTIVITY_CORPUS.values() for activity in activities
]

STOPWORDS = {
    "a", "an", "and", "at", "for", "from", "go", "going", "in", "into",
    "is", "it", "my", "of", "on", "or", "the", "to", "with", "want",
    "plan", "doing", "do", "need", "some", "something",
}

ONLINE_HINTS = {"online", "delivery", "website", "app", "ecommerce"}
PHYSICAL_STORE_HINTS = {
    "shop",
    "store",
    "market",
    "mall",
    "supermarket",
    "tobacco",
    "pharmacy",
    "kiosk",
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-z]+\b", _normalize(text)))


def _content_tokens(text: str) -> set[str]:
    return {token for token in _tokenize(text) if len(token) >= 3 and token not in STOPWORDS}


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


def _build_token_priors() -> dict[str, dict[str, float]]:
    counts: dict[str, dict[str, int]] = {}
    for label, activities in ACTIVITY_CORPUS.items():
        for phrase in activities:
            for token in _tokenize(phrase):
                if len(token) < 3:
                    continue
                if token not in counts:
                    counts[token] = {"Indoor": 0, "Outdoor": 0}
                counts[token][label] += 1

    priors: dict[str, dict[str, float]] = {}
    for token, token_counts in counts.items():
        total = token_counts["Indoor"] + token_counts["Outdoor"]
        if total == 0:
            continue
        priors[token] = {
            "Indoor": token_counts["Indoor"] / total,
            "Outdoor": token_counts["Outdoor"] / total,
        }
    return priors


TOKEN_PRIORS = _build_token_priors()


@lru_cache(maxsize=256)
def _fetch_runtime_slang_context(term: str) -> str:
    """Fetch lightweight web context for unfamiliar/slang terms at runtime."""
    normalized = _normalize(term)
    if not normalized:
        return ""

    chunks: list[str] = []

    try:
        urban = requests.get(
            "https://api.urbandictionary.com/v0/define",
            params={"term": normalized},
            timeout=1.8,
        )
        if urban.ok:
            data = urban.json()
            for item in (data.get("list") or [])[:2]:
                definition = item.get("definition", "")
                example = item.get("example", "")
                chunks.append(f"{definition} {example}")
    except Exception:
        pass

    try:
        related = requests.get(
            "https://api.datamuse.com/words",
            params={"ml": normalized, "max": 10},
            timeout=1.5,
        )
        if related.ok:
            words = [entry.get("word", "") for entry in related.json()[:10]]
            chunks.extend(words)
    except Exception:
        pass

    return _normalize(" ".join(chunks))


def _token_prior_votes(tokens: set[str]) -> tuple[float, float]:
    indoor_vote = 0.0
    outdoor_vote = 0.0
    for token in tokens:
        prior = TOKEN_PRIORS.get(token)
        if not prior:
            continue
        indoor_vote += prior["Indoor"]
        outdoor_vote += prior["Outdoor"]
    return indoor_vote, outdoor_vote


def classify_with_dictionary(
    activity_text: str,
    use_web_enrichment: bool = False,
) -> tuple[str, float, Optional[str]]:
    """Classify activity as Indoor/Outdoor by matching against imported ACTIVITY_CORPUS."""
    normalized_input = _normalize(activity_text)
    if not normalized_input:
        return "Indoor", 0.0, None

    runtime_context = _fetch_runtime_slang_context(normalized_input) if use_web_enrichment else ""
    enriched_input = _normalize(f"{normalized_input} {runtime_context}")
    input_tokens = _tokenize(enriched_input)
    content_input_tokens = _content_tokens(enriched_input)
    has_online_hint = len(input_tokens & ONLINE_HINTS) > 0
    has_physical_store_hint = len(input_tokens & PHYSICAL_STORE_HINTS) > 0
    errand_action_hints = {"go", "going", "get", "buy", "purchase", "from", "to", "pick", "pickup"}

    if has_physical_store_hint and not has_online_hint and (input_tokens & errand_action_hints):
        return "Outdoor", 0.88, "physical store errand"

    best_label = "Indoor"
    best_phrase: Optional[str] = None
    best_score = 0.0

    indoor_prior, outdoor_prior = _token_prior_votes(content_input_tokens)
    prior_total = indoor_prior + outdoor_prior
    prior_confidence = max(indoor_prior, outdoor_prior) / prior_total if prior_total > 0 else 0.0
    prior_label = "Outdoor" if outdoor_prior > indoor_prior else "Indoor"

    for label, activities in ACTIVITY_CORPUS.items():
        for phrase in activities:
            for variant in _phrase_variants(label, phrase):
                phrase_tokens = _tokenize(variant)
                phrase_content_tokens = _content_tokens(variant)
                token_overlap = 0.0
                if content_input_tokens and phrase_content_tokens:
                    token_overlap = len(content_input_tokens & phrase_content_tokens) / len(
                        content_input_tokens | phrase_content_tokens
                    )
                elif input_tokens and phrase_tokens:
                    token_overlap = len(input_tokens & phrase_tokens) / len(input_tokens | phrase_tokens)

                char_similarity = calculate_similarity(normalized_input, variant)
                starts_with_bonus = 0.0
                if token_overlap > 0.0 and (normalized_input.startswith(variant) or variant.startswith(normalized_input)):
                    starts_with_bonus = 0.04

                environment_bonus = 0.0
                if ("outside" in input_tokens or "outdoor" in input_tokens) and label == "Outdoor":
                    environment_bonus += 0.04
                if ("inside" in input_tokens or "indoor" in input_tokens or "home" in input_tokens) and label == "Indoor":
                    environment_bonus += 0.04

                score = token_overlap * 0.70 + char_similarity * 0.18 + starts_with_bonus + environment_bonus

                # Do not let online-shopping phrases dominate physical errands.
                if ("online" in phrase_tokens) and not has_online_hint:
                    score *= 0.55

                # Physical store errands are generally outside-home movement.
                if has_physical_store_hint and not has_online_hint and label == "Outdoor":
                    score += 0.10

                # Prevent misleading matches driven mostly by character similarity
                # (e.g. unrelated slang accidentally close to a corpus phrase).
                if token_overlap == 0.0 and starts_with_bonus == 0.0:
                    score = min(score, 0.34)

                if score > best_score:
                    best_score = score
                    best_label = label
                    best_phrase = phrase

    # Blend phrase matching with corpus-derived token priors for less rigid behavior.
    if prior_confidence >= 0.58 and prior_confidence > best_score:
        best_label = prior_label
        best_score = min(0.99, prior_confidence)
        best_phrase = best_phrase or "token-prior consensus"
    elif prior_total > 0:
        best_score = min(0.99, (best_score * 0.8) + (prior_confidence * 0.2))

    return best_label, min(best_score, 0.99), best_phrase


def calculate_similarity(input_str: str, candidate: str) -> float:
    return SequenceMatcher(None, input_str.lower(), candidate.lower()).ratio()


def extract_words(text: str) -> list[str]:
    return re.findall(r'\b[a-z]+\b', text.lower())


def suggest_activity(broken_input: str) -> Optional[Tuple[str, float, str]]:
    if not broken_input or len(broken_input.strip()) < 3:
        return None

    cleaned = broken_input.strip().lower()
    input_content = _content_tokens(cleaned)
    input_tokens = _tokenize(cleaned)

    has_online_hint = len(input_tokens & ONLINE_HINTS) > 0
    has_physical_store_hint = len(input_tokens & PHYSICAL_STORE_HINTS) > 0
    if has_physical_store_hint and not has_online_hint:
        if "tobacco" in input_tokens or "cigarette" in input_tokens or "cigarettes" in input_tokens:
            return ("going to tobacco shop", 0.86, "Outdoor")
        return ("going to store", 0.82, "Outdoor")

    close_matches = get_close_matches(cleaned, ALL_ACTIVITIES, n=5, cutoff=0.52)

    best_match = None
    best_score = 0.0
    
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
        viable = []
        for candidate in close_matches:
            candidate_tokens = _content_tokens(candidate)
            overlap = len(input_content & candidate_tokens) if input_content and candidate_tokens else 0
            similarity = calculate_similarity(cleaned, candidate)
            if overlap > 0 or similarity >= 0.86:
                viable.append((candidate, similarity, overlap))

        if not viable:
            return None

        suggestion, confidence, _ = max(viable, key=lambda item: (item[2], item[1]))
    
    classification = None
    for cat, activities in ACTIVITY_CORPUS.items():
        if suggestion in activities:
            classification = cat
            break
    
    if not classification:
        classification = "Indoor"

    # Avoid low-quality hints from unrelated phrases.
    if confidence < 0.58:
        return None

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
