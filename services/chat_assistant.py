from __future__ import annotations

from datetime import datetime, timedelta
import json
import os
import re
from typing import Any, Optional


DAY_INDEX = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _parse_time(text: str) -> Optional[str]:
    text_lower = text.lower()
    match = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b", text_lower)
    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)
    suffix = match.group(3)

    if suffix == "pm" and hour < 12:
        hour += 12
    if suffix == "am" and hour == 12:
        hour = 0

    if hour > 23 or minute > 59:
        return None

    return f"{hour:02d}:{minute:02d}"


def _parse_date(text: str, today: datetime) -> Optional[str]:
    lowered = text.lower()

    if "today" in lowered:
        return today.date().isoformat()
    if "tomorrow" in lowered:
        return (today.date() + timedelta(days=1)).isoformat()

    explicit = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", lowered)
    if explicit:
        return f"{explicit.group(1)}-{explicit.group(2)}-{explicit.group(3)}"

    for day_name, target_index in DAY_INDEX.items():
        if day_name in lowered:
            days_ahead = (target_index - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return (today.date() + timedelta(days=days_ahead)).isoformat()

    return None


def _extract_task(text: str) -> Optional[str]:
    lowered = text.lower()

    explicit_patterns = [
        r"(?:task is|task:|add task|create task|schedule)\s+(.+)",
        r"(?:i need to|i want to|i have to)\s+(.+)",
    ]

    def clean_task(value: str) -> str:
        cleaned = _normalize_space(value)
        cleaned = re.sub(
            r"\b(on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow|\d{4}-\d{2}-\d{2}))\b.*$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(
            r"\b(at\s+\d{1,2}(?::\d{2})?\s*(am|pm)?)\b.*$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        return _normalize_space(cleaned)

    for pattern in explicit_patterns:
        match = re.search(pattern, lowered)
        if match:
            value = clean_task(match.group(1))
            if value:
                return value[:120]

    if len(lowered) <= 120 and any(token in lowered for token in ["gym", "work", "study", "meeting", "call", "homework", "shopping", "run", "walk"]):
        return clean_task(text)[:120]

    return None


def _is_yes(text: str) -> bool:
    return bool(re.search(r"\b(yes|yep|sure|ok|okay|confirm|do it|sounds good)\b", text.lower()))


def _is_no(text: str) -> bool:
    return bool(re.search(r"\b(no|nah|cancel|stop|dont|don't)\b", text.lower()))


def _local_assistant_response(messages: list[dict[str, str]], draft: dict[str, Any], today_iso: str) -> dict[str, Any]:
    today = datetime.fromisoformat(today_iso)
    last_user = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user = message.get("content", "")
            break

    next_draft = {
        "task_title": draft.get("task_title"),
        "date": draft.get("date"),
        "time": draft.get("time"),
        "notes": draft.get("notes"),
    }

    parsed_task = _extract_task(last_user)
    parsed_date = _parse_date(last_user, today)
    parsed_time = _parse_time(last_user)

    if parsed_task:
        next_draft["task_title"] = parsed_task
    if parsed_date:
        next_draft["date"] = parsed_date
    if parsed_time:
        next_draft["time"] = parsed_time

    missing = [
        field
        for field in ["task_title", "date", "time"]
        if not next_draft.get(field)
    ]

    if _is_no(last_user):
        return {
            "assistant_message": "Okay, I cancelled that draft. Tell me the task, day, and time whenever you are ready.",
            "draft": {"task_title": None, "date": None, "time": None, "notes": None},
            "missing_fields": ["task_title", "date", "time"],
            "requires_confirmation": False,
            "create_task": False,
            "navigate_to": "chat",
            "reset_draft": True,
        }

    if missing:
        prompts = {
            "task_title": "What task should I add?",
            "date": "Which day should I schedule it for? You can say today, tomorrow, Monday, or YYYY-MM-DD.",
            "time": "What time should I schedule it?",
        }
        question = prompts[missing[0]]
        return {
            "assistant_message": question,
            "draft": next_draft,
            "missing_fields": missing,
            "requires_confirmation": False,
            "create_task": False,
            "navigate_to": "chat",
            "reset_draft": False,
        }

    if _is_yes(last_user):
        return {
            "assistant_message": "Great, I will add it to your Todo list and Timetable now.",
            "draft": next_draft,
            "missing_fields": [],
            "requires_confirmation": False,
            "create_task": True,
            "navigate_to": "timetable",
            "reset_draft": True,
        }

    return {
        "assistant_message": (
            f"Please confirm: add '{next_draft['task_title']}' on {next_draft['date']} at {next_draft['time']}?"
        ),
        "draft": next_draft,
        "missing_fields": [],
        "requires_confirmation": True,
        "create_task": False,
        "navigate_to": "chat",
        "reset_draft": False,
    }


def chat_assistant_reply(
    messages: list[dict[str, str]],
    draft: dict[str, Any],
    today_iso: str,
    use_openai: bool = True,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
    if not use_openai or not api_key:
        return _local_assistant_response(messages, draft, today_iso)

    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    system_prompt = (
        "You are SkyCoach Chat Assistant. Help users operate the app conversationally. "
        "Collect required fields for scheduling tasks: task_title, date (YYYY-MM-DD), time (HH:MM 24h). "
        "If any field is missing, ask exactly one clear question for the next missing field. "
        "When all fields are present, ask for explicit user confirmation before creation. "
        "If user confirms, set create_task=true and reset_draft=true. "
        "If user cancels, clear the draft and ask to restart. "
        "Return JSON only with keys: assistant_message, draft, missing_fields, requires_confirmation, create_task, navigate_to, reset_draft. "
        "navigate_to must be one of dashboard, todo, timetable, planner, chat."
    )

    payload = {
        "today": today_iso,
        "current_draft": {
            "task_title": draft.get("task_title"),
            "date": draft.get("date"),
            "time": draft.get("time"),
            "notes": draft.get("notes"),
        },
        "conversation": messages,
    }

    response = client.chat.completions.create(
        model=openai_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json.dumps(payload)},
        ],
        response_format={"type": "json_object"},
        max_tokens=320,
        temperature=0.2,
    )

    content = response.choices[0].message.content or "{}"
    parsed = json.loads(content)

    draft_result = parsed.get("draft", {}) or {}
    return {
        "assistant_message": str(parsed.get("assistant_message", "Please share the task, day, and time.")),
        "draft": {
            "task_title": draft_result.get("task_title"),
            "date": draft_result.get("date"),
            "time": draft_result.get("time"),
            "notes": draft_result.get("notes"),
        },
        "missing_fields": parsed.get("missing_fields", []),
        "requires_confirmation": bool(parsed.get("requires_confirmation", False)),
        "create_task": bool(parsed.get("create_task", False)),
        "navigate_to": parsed.get("navigate_to", "chat"),
        "reset_draft": bool(parsed.get("reset_draft", False)),
    }