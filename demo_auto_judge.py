#!/usr/bin/env python
"""Auto-judge feature demonstration."""

from services.ai_engine import analyze_task_fallback

# Test broken input with auto-judge
task = analyze_task_fallback('doing homewo')
print('===== AUTO-JUDGE FEATURE DEMO =====')
print(f'User Input: "doing homewo"')
print()
print('Initial Analysis:')
print(f'  Activity: {task.activity}')
print(f'  Confidence: {task.confidence:.1%}')
print(f'  Needs Clarification: {task.needs_clarification}')
print(f'  Issue: {task.issue}')
print()
print('Auto-Judge Suggestion:')
print(f'  Suggested Activity: {task.suggested_activity}')
print(f'  Suggested Class: {task.suggested_classification}')
print(f'  Suggestion Confidence: {task.suggestion_confidence:.1%}')
print()
print('Result: User can accept suggestion or try again with clarified input')
print()
print('=' * 50)
