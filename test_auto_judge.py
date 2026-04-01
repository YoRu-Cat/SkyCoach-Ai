#!/usr/bin/env python
"""Test auto-judge feature."""

from services.ai_engine import analyze_task_fallback

test_cases = [
    'doing homewo',
    'wash car',
    'play socc',
    'biking',
    'cooking diner',
]

print('Auto-Judge Feature Test Results:')
print('=' * 70)

for test in test_cases:
    result = analyze_task_fallback(test)
    print(f'\nInput: "{test}"')
    print(f'  Activity: {result.activity}')
    print(f'  Classification: {result.classification}')
    print(f'  Needs Clarification: {result.needs_clarification}')
    if result.suggested_activity:
        print(f'  ✓ Auto-Judge Suggestion: {result.suggested_activity}')
        print(f'  ✓ Suggestion Confidence: {result.suggestion_confidence:.2f}')
    print(f'  Confidence: {result.confidence:.2f}')
