# Auto-Judge Feature

## Purpose

Auto-judge is the local suggestion layer used during task analysis.

It helps with:

- incomplete inputs
- misspellings
- ambiguous activity phrases

## Current Behavior

- Runs locally, no OpenAI dependency.
- Uses dictionary and context-aware matching.
- Returns suggestion metadata used by frontend for autocorrect-like guidance.

## Output Fields

- `needs_clarification`
- `issue`
- `suggested_activity`
- `suggested_classification`
- `suggestion_confidence`

## Example Request

```json
{
  "text": "doing homewo",
  "use_openai": false
}
```

## Example Response Fragment

```json
{
  "needs_clarification": true,
  "issue": "Input looks unfinished or misspelled",
  "suggested_activity": "doing homework",
  "suggested_classification": "Indoor",
  "suggestion_confidence": 0.92
}
```
