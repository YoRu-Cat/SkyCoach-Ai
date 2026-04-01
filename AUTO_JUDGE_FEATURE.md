"""Auto-Judge Feature Documentation and Examples"""

# Auto-Judge Feature

## Overview

The Auto-Judge feature intelligently suggests corrections for incomplete, misspelled, or broken activity inputs. When a user enters a partial or unclear activity description, the system:

1. **Detects** that the input needs clarification (too short, misspelled, unfinished)
2. **Analyzes** the input using fuzzy string matching and word overlap algorithms
3. **Suggests** the most likely intended activity with a confidence score
4. **Displays** the suggestion in the UI for user confirmation

## Use Cases

### Before Auto-Judge

User types: "doing homewo"
System response: "Needs clarification" ❌

### After Auto-Judge

User types: "doing homewo"
System response:

- Detected issue: "Input looks unfinished or misspelled"
- Auto-Judge Suggestion: "doing homework" (92% confidence)
- User can accept or retry with clearer input ✓

## How It Works

### Algorithm

1. **Fuzzy Matching**: Looks for close string matches in activity corpus
   - Uses difflib.get_close_matches() for direct substring matching
2. **Word Overlap Analysis**: When fuzzy match fails
   - Extracts meaningful words from both input and activities
   - Scores activities based on word overlap (65% weight) + character similarity (35%)
   - Returns highest-scoring activity if confidence > 40%

3. **Classification**: Automatically classifies suggested activity as Indoor/Outdoor
   - Based on corpus lookup

### Activity Corpus

**Outdoor Activities (50+)**

- sports: playing soccer, tennis, basketball
- recreation: hiking, biking, swimming, fishing
- maintenance: car washing, gardening, lawn mowing
- etc.

**Indoor Activities (80+)**

- learning: doing homework, studying, researching
- entertainment: gaming, watching movies, reading
- work: coding, designing, office work
- cooking: cooking, baking, meal prep
- cleaning: house cleaning, laundry, organizing
- etc.

## Example Results

| Input           | Suggestion       | Confidence |
| --------------- | ---------------- | ---------- |
| "doing homewo"  | "doing homework" | 92%        |
| "play socc"     | "playing soccer" | 78%        |
| "biking"        | "biking"         | 100%       |
| "wash car"      | "washing car"    | 100%       |
| "cooking diner" | "cooking meal"   | 72%        |

## API Response

When an input needs clarification, the API response includes:

```json
{
  "activity": "Needs clarification",
  "confidence": 0.15,
  "needs_clarification": true,
  "issue": "Input looks unfinished or misspelled",
  "suggested_activity": "doing homework",
  "suggested_classification": "Indoor",
  "suggestion_confidence": 0.92
}
```

## UI Display

In the Activity Analysis card:

```
🧠 Activity Analysis
⚠️ Needs clarification
━━━━━━━━━━━━━━━━━━
Original input: "doing homewo"
Cleaned text: "Doing Homewo"
Identified activity: "Needs clarification"
Confidence: 15%
Issue: "Input looks unfinished or misspelled"

AUTO-JUDGE SUGGESTION
━━━━━━━━━━━━━━━━━━
Likely activity: "doing homework"
Classification: "Indoor"
Suggestion confidence: "92%"
```

## Technical Implementation

### Files

- **services/auto_judge.py**: Core fuzzy matching engine
  - `suggest_activity()`: Main suggestion function
  - `auto_judge_input()`: Complete judgment wrapper
  - `ACTIVITY_CORPUS`: Dict with 130+ activities

- **services/ai_engine.py**: Integration into analysis pipeline
  - Both `analyze_task_openai()` and `analyze_task_fallback()` use auto_judge

- **models/data_classes.py**: Fields in TaskAnalysis
  - `suggested_activity`, `suggested_classification`, `suggestion_confidence`

- **components/cards.py**: UI rendering
  - Shows suggestion section in render_analysis_card()

- **backend/schemas/models.py**: API response schema
  - TaskAnalysisResponse includes suggestion fields

- **backend/api/routes.py**: API integration
  - All endpoints return suggestions in response

## Performance

- **Suggestion lookup**: <50ms (no external API calls)
- **Word analysis**: <20ms for 130 activities
- **Total latency**: Adds <100ms to analysis request

## Extensibility

To add more activities to the corpus:

```python
# In services/auto_judge.py, add to ACTIVITY_CORPUS:

ACTIVITY_CORPUS = {
    "Outdoor": [
        # ... existing activities ...
        "new outdoor activity",
    ],
    "Indoor": [
        # ... existing activities ...
        "new indoor activity",
    ]
}
```

## Edge Cases Handled

- Single-word inputs: "biking" → matches full activity
- Missing verbs: "car" → suggests car-related activities
- Typos: "homewo" → "homework", "socc" → "soccer"
- Incomplete verbs: "play" → "playing soccer", "wash" → "washing car"
- Phonetic similarities: Standard difflib similarity metric

## Future Enhancements

1. Machine learning ranking (weight suggestions by user acceptance)
2. Context-aware suggestions (time of day, weather, location)
3. Multi-word suggestions with ranking
4. User dictionary for custom activities
5. Feedback loop to improve corpus

## Testing

Run the test suite:

```bash
python test_auto_judge.py  # Basic functionality tests
python demo_auto_judge.py  # Interactive demonstration
```

Or test the API:

```bash
curl -X POST http://localhost:8000/api/analyze-task \
  -H "Content-Type: application/json" \
  -d '{"text": "doing homewo", "use_openai": false}'
```
