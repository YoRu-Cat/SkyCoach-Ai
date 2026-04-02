# Auto-Judge Module

**Location:** `services/auto_judge.py`

## Purpose
Suggests likely intended activities from incomplete, broken, or misspelled user input. Uses fuzzy matching and word overlap heuristics.

## Key Functions

### `suggest_activity(broken_input)`
Analyzes incomplete input and suggests the most likely intended activity.  
**Input:** Incomplete activity description  
**Output:** Tuple of (activity, confidence, classification) or None

### `auto_judge_input(text)`
Main entry point for auto-judgment.  
**Output:** Dictionary with:
- `original`: Original input text
- `is_broken`: Boolean indicating if input was incomplete
- `suggestion`: Recommended activity
- `confidence`: Confidence score (0.0-1.0)
- `classification`: "Indoor" or "Outdoor"

### Helper Functions
- `calculate_similarity()` - String similarity ratio using SequenceMatcher
- `extract_words()` - Extracts meaningful words from text

## Activity Corpus
Comprehensive list of 100+ activities organized by type:

**Outdoor (50+ activities):**  
Soccer, football, hiking, cycling, swimming, basketball, volleyball, tennis, gardening, yard work, dog walking, camping, fishing, golf, etc.

**Indoor (50+ activities):**  
Homework, studying, gaming, reading, cooking, baking, art, crafts, yoga, meditation, board games, music, dancing, cleaning, shopping, etc.

## Matching Algorithm
1. Use Python's `difflib.get_close_matches()` with 0.4 cutoff
2. If no close matches, calculate word overlap + character similarity
3. Return suggestion with confidence score

## Confidence Scoring
- Based on string similarity and word overlap ratio
- Returns 0.0-1.0 float value
- Threshold of 0.4 required for positive suggestion

## Use Cases
- "play socc" → suggests "playing soccer" (Outdoor)
- "doing homewo" → suggests "doing homework" (Indoor)  
- "wash car" → suggests "washing car" (Outdoor)
