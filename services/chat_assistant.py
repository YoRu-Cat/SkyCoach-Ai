from __future__ import annotations

from datetime import datetime, timedelta
from difflib import get_close_matches
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

COMMON_WORD_FIXES = {
    "shoping": "shopping",
    "grcey": "grocery",
    "grocey": "grocery",
    "wrk": "work",
    "hmework": "homework",
}


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _normalize_typos(text: str) -> str:
    words = re.findall(r"[a-zA-Z']+|[^a-zA-Z']+", text)
    corrected: list[str] = []
    for token in words:
        key = token.lower()
        if key in COMMON_WORD_FIXES:
            fixed = COMMON_WORD_FIXES[key]
            if token[:1].isupper():
                fixed = fixed.capitalize()
            corrected.append(fixed)
        else:
            corrected.append(token)
    return "".join(corrected)


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9\s]", " ", text.lower())).strip()


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


def _parse_part_of_day(text: str) -> Optional[str]:
    lowered = text.lower()
    if "morning" in lowered:
        return "09:00"
    if "afternoon" in lowered:
        return "14:00"
    if "evening" in lowered or "tonight" in lowered:
        return "19:00"
    return None


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
    normalized_text = _normalize_typos(text)
    lowered = normalized_text.lower()

    explicit_patterns = [
        r"(?:can you|could you|would you|please)\s+(?:add|create|schedule)\s+(.+)",
        r"(?:add|create|schedule)\s+(.+)",
        r"(?:task is|task:|add task|create task|schedule)\s+(.+)",
        r"(?:i need to|i want to|i have to)\s+(.+)",
    ]

    def clean_task(value: str) -> str:
        cleaned = _normalize_space(value)
        cleaned = re.sub(r"\bif\b.+$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\bunless\b.+$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(
            r"\b(on\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday|today|tomorrow|\d{4}-\d{2}-\d{2}))\b.*$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r"\b(at\s+\d{1,2}(?::\d{2})?\s*(am|pm)?)\b.*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(in the\s+(morning|afternoon|evening)|tonight)\b.*$", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\b(please|for me)\b", "", cleaned, flags=re.IGNORECASE)
        return _normalize_space(cleaned)

    for pattern in explicit_patterns:
        match = re.search(pattern, lowered)
        if match:
            value = clean_task(match.group(1))
            if value:
                return value[:120]

    if len(lowered) <= 120 and any(token in lowered for token in ["gym", "work", "study", "meeting", "call", "homework", "shopping", "run", "walk"]):
        return clean_task(normalized_text)[:120]

    return None


def _extract_notes(text: str) -> Optional[str]:
    normalized_text = _normalize_typos(text)
    lowered = normalized_text.lower()
    conditional = re.search(r"\b(if|unless)\b\s+(.+)", lowered)
    if conditional:
        clause = _normalize_space(conditional.group(0))
        return clause[:140]
    return None


def _is_yes(text: str) -> bool:
    return bool(re.search(r"\b(yes|yep|sure|ok|okay|confirm|do it|sounds good)\b", text.lower()))


def _is_no(text: str) -> bool:
    return bool(re.search(r"\b(no|nah|cancel|stop|dont|don't)\b", text.lower()))


def _resolve_task_target(text: str, task_context: list[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not task_context:
        return None

    lowered = _normalize_text(text)
    titles = [str(task.get("title", "")) for task in task_context]
    normalized_titles = [_normalize_text(title) for title in titles]

    best_index = -1
    best_len = 0
    for idx, title in enumerate(normalized_titles):
        if title and title in lowered and len(title) > best_len:
            best_index = idx
            best_len = len(title)

    if best_index >= 0:
        return task_context[best_index]

    cleaned = re.sub(r"\b(remove|delete|complete|finish|done|undone|uncomplete|reopen|reschedule|move|task|from|todo|list|there|it)\b", " ", lowered)
    cleaned = _normalize_space(cleaned)
    if cleaned:
        candidate = get_close_matches(cleaned, normalized_titles, n=1, cutoff=0.45)
        if candidate:
            idx = normalized_titles.index(candidate[0])
            return task_context[idx]

    return None


def _detect_control_intent(text: str) -> str:
    lowered = text.lower()
    if re.search(r"\b(remove|delete)\b", lowered):
        return "remove"
    if re.search(r"\b(uncomplete|undo|reopen|not done|incomplete|mark\s+pending)\b", lowered):
        return "uncomplete"
    if re.search(r"\b(mark|set)\b.*\b(done|complete|completed|finished)\b", lowered) or re.search(r"\b(complete|finish)\b", lowered):
        return "complete"
    if re.search(r"\b(reschedule|move)\b", lowered):
        return "reschedule"
    if re.search(r"\b(clear)\b.*\b(completed|done)\b", lowered):
        return "clear_completed"
    if re.search(r"\b(show|list)\b.*\b(tasks|todo)\b", lowered):
        return "list"
    if re.search(r"\b(go to|open|show)\b.*\b(dashboard|todo|timetable|planner|chat)\b", lowered):
        return "navigate"
    return "create"


def _detect_navigation_target(text: str) -> str:
    lowered = text.lower()
    for target in ["dashboard", "todo", "timetable", "planner", "chat"]:
        if target in lowered:
            return target
    return "chat"


def _infer_pending_intent(messages: list[dict[str, str]]) -> Optional[str]:
    """Infer pending control intent from recent turns to avoid follow-up loops."""
    recent_assistant = ""
    recent_user_messages: list[str] = []

    for message in reversed(messages):
        role = message.get("role")
        content = message.get("content", "")
        if role == "assistant" and not recent_assistant:
            recent_assistant = content.lower()
        elif role == "user":
            recent_user_messages.append(content)
        if recent_assistant and len(recent_user_messages) >= 3:
            break

    if "which task should i target" not in recent_assistant and "please provide both day and time" not in recent_assistant:
        return None

    for user_message in recent_user_messages:
        inferred = _detect_control_intent(user_message)
        if inferred != "create":
            return inferred

    return None


def _should_use_local_controller(
    messages: list[dict[str, str]],
    draft: dict[str, Any],
    task_context: list[dict[str, Any]],
) -> bool:
    last_user = ""
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user = message.get("content", "")
            break

    if not last_user:
        return False

    lowered = last_user.lower()
    if any(
        token in lowered
        for token in [
            "remove",
            "delete",
            "complete",
            "finish",
            "uncomplete",
            "reopen",
            "reschedule",
            "move",
            "clear completed",
            "list tasks",
            "show tasks",
            "open todo",
            "open timetable",
            "open planner",
            "open dashboard",
            "go to todo",
            "go to timetable",
            "go to planner",
            "go to dashboard",
            "go to chat",
        ]
    ):
        return True

    if any(draft.get(field) for field in ["task_title", "date", "time", "notes"]):
        if _is_yes(last_user) or _is_no(last_user):
            return True
        if re.search(r"\b(today|tomorrow|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d{4}-\d{2}-\d{2}|\d{1,2}(?::\d{2})?\s*(am|pm)?)\b", lowered):
            return True

    if task_context and re.search(r"\b(add|create|schedule|remove|delete|complete|finish|undo|reopen|reschedule|move)\b", lowered):
        return True

    return False


def _base_response(draft: dict[str, Any], message: str) -> dict[str, Any]:
    return {
        "assistant_message": message,
        "draft": draft,
        "missing_fields": [],
        "requires_confirmation": False,
        "create_task": False,
        "remove_task_id": None,
        "complete_task_id": None,
        "uncomplete_task_id": None,
        "reschedule_task_id": None,
        "reschedule_date": None,
        "reschedule_time": None,
        "clear_completed": False,
        "navigate_to": "chat",
        "reset_draft": False,
    }


def _local_assistant_response(
    messages: list[dict[str, str]],
    draft: dict[str, Any],
    today_iso: str,
    task_context: list[dict[str, Any]],
) -> dict[str, Any]:
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

    pending_intent = _infer_pending_intent(messages)
    intent = pending_intent or _detect_control_intent(last_user)

    if intent == "navigate":
        target = _detect_navigation_target(last_user)
        response = _base_response(next_draft, f"Sure, opening {target} view.")
        response["navigate_to"] = target
        return response

    if intent == "list":
        if not task_context:
            listing = "You have no tasks yet."
        else:
            listing = "Your tasks: " + "; ".join(
                [f"{task.get('title', 'Untitled')} ({'done' if task.get('completed') else 'pending'})" for task in task_context[:8]]
            )
        response = _base_response(next_draft, listing)
        response["navigate_to"] = "todo"
        return response

    if intent == "clear_completed":
        response = _base_response(next_draft, "Done. Cleared all completed tasks.")
        response["clear_completed"] = True
        response["navigate_to"] = "todo"
        return response

    if intent in {"remove", "complete", "uncomplete", "reschedule"}:
        target_task = _resolve_task_target(last_user, task_context)
        if not target_task:
            if task_context:
                preview = ", ".join([str(task.get("title", "Untitled")) for task in task_context[:6]])
                return _base_response(next_draft, f"I can do that. Which task should I target? Current tasks: {preview}")
            return _base_response(next_draft, "I can do that. Which task should I target?")

        target_id = str(target_task.get("id"))
        target_title = str(target_task.get("title", "task"))

        if intent == "remove":
            response = _base_response(next_draft, f"Removed '{target_title}' from your Todo and Timetable.")
            response["remove_task_id"] = target_id
            response["navigate_to"] = "todo"
            return response

        if intent == "complete":
            response = _base_response(next_draft, f"Marked '{target_title}' as completed.")
            response["complete_task_id"] = target_id
            response["navigate_to"] = "todo"
            return response

        if intent == "uncomplete":
            response = _base_response(next_draft, f"Marked '{target_title}' as pending again.")
            response["uncomplete_task_id"] = target_id
            response["navigate_to"] = "todo"
            return response

        new_date = _parse_date(last_user, today)
        new_time = _parse_time(last_user) or _parse_part_of_day(last_user)
        if not new_date or not new_time:
            return _base_response(next_draft, "I can reschedule it. Please provide both day and time.")

        response = _base_response(next_draft, f"Rescheduled '{target_title}' to {new_date} at {new_time}.")
        response["reschedule_task_id"] = target_id
        response["reschedule_date"] = new_date
        response["reschedule_time"] = new_time
        response["navigate_to"] = "timetable"
        return response

    parsed_task = _extract_task(last_user)
    parsed_date = _parse_date(last_user, today)
    parsed_time = _parse_time(last_user) or _parse_part_of_day(last_user)
    parsed_notes = _extract_notes(last_user)

    if parsed_task:
        next_draft["task_title"] = parsed_task
    if parsed_date:
        next_draft["date"] = parsed_date
    if parsed_time:
        next_draft["time"] = parsed_time
    if parsed_notes:
        next_draft["notes"] = parsed_notes

    missing = [field for field in ["task_title", "date", "time"] if not next_draft.get(field)]

    if _is_no(last_user):
        response = _base_response(
            {"task_title": None, "date": None, "time": None, "notes": None},
            "Okay, I cancelled that draft. Tell me the task, day, and time whenever you are ready.",
        )
        response["missing_fields"] = ["task_title", "date", "time"]
        response["reset_draft"] = True
        return response

    if missing:
        if missing[0] == "task_title":
            question = "I can do that. What task should I add?"
        elif missing[0] == "date":
            if next_draft.get("task_title"):
                question = (
                    f"Got it, I'll add '{next_draft['task_title']}'. Which day should I schedule it for? "
                    "You can say today, tomorrow, Monday, or YYYY-MM-DD."
                )
            else:
                question = "Which day should I schedule it for?"
        else:
            task_text = f"'{next_draft['task_title']}'" if next_draft.get("task_title") else "that"
            day_text = f" on {next_draft['date']}" if next_draft.get("date") else ""
            question = f"Great, what time should I schedule {task_text}{day_text}?"

        response = _base_response(next_draft, question)
        response["missing_fields"] = missing
        return response

    if _is_yes(last_user):
        response = _base_response(next_draft, "Great, I will add it to your Todo list and Timetable now.")
        response["create_task"] = True
        response["navigate_to"] = "timetable"
        response["reset_draft"] = True
        return response

    response = _base_response(
        next_draft,
        (
            f"I understood: add '{next_draft['task_title']}' on {next_draft['date']} at {next_draft['time']}. "
            f"{('Notes: ' + next_draft['notes'] + '. ') if next_draft.get('notes') else ''}"
            "Should I create it now?"
        ),
    )
    response["requires_confirmation"] = True
    return response


def chat_assistant_reply(
    messages: list[dict[str, str]],
    draft: dict[str, Any],
    task_context: Optional[list[dict[str, Any]]] = None,
    today_iso: str = "",
    use_openai: bool = True,
    openai_api_key: Optional[str] = None,
    openai_model: str = "gpt-4o-mini",
) -> dict[str, Any]:
    task_context = task_context or []
    api_key = openai_api_key or os.getenv("OPENAI_API_KEY")

    if not today_iso:
        today_iso = datetime.now().date().isoformat()

    if not use_openai or not api_key or _should_use_local_controller(messages, draft, task_context):
        return _local_assistant_response(messages, draft, today_iso, task_context)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        system_prompt = (
            "You are SkyCoach Chat Assistant. Help users operate the app conversationally like a real assistant. "
            "You can fully control the app: create tasks, remove tasks, mark complete/incomplete, reschedule tasks, clear completed tasks, list tasks, and navigate views. "
            "Collect required fields for creating or rescheduling tasks: task_title, date (YYYY-MM-DD), time (HH:MM 24h). "
            "If fields are missing for create/reschedule, ask one clear follow-up. "
            "When creating a new task with all fields present, ask for explicit confirmation before create_task=true. "
            "For remove/complete/uncomplete/reschedule, prefer using task IDs from task_context. "
            "Return JSON only with keys: assistant_message, draft, missing_fields, requires_confirmation, create_task, remove_task_id, complete_task_id, uncomplete_task_id, reschedule_task_id, reschedule_date, reschedule_time, clear_completed, navigate_to, reset_draft. "
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
            "task_context": task_context,
            "conversation": messages,
        }

        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(payload)},
            ],
            response_format={"type": "json_object"},
            max_tokens=420,
            temperature=0.2,
        )

        content = response.choices[0].message.content or "{}"
        parsed = json.loads(content)

        draft_result = parsed.get("draft", {}) or {}
        return {
            "assistant_message": str(parsed.get("assistant_message", "Tell me what you want me to do.")),
            "draft": {
                "task_title": draft_result.get("task_title"),
                "date": draft_result.get("date"),
                "time": draft_result.get("time"),
                "notes": draft_result.get("notes"),
            },
            "missing_fields": parsed.get("missing_fields", []),
            "requires_confirmation": bool(parsed.get("requires_confirmation", False)),
            "create_task": bool(parsed.get("create_task", False)),
            "remove_task_id": parsed.get("remove_task_id"),
            "complete_task_id": parsed.get("complete_task_id"),
            "uncomplete_task_id": parsed.get("uncomplete_task_id"),
            "reschedule_task_id": parsed.get("reschedule_task_id"),
            "reschedule_date": parsed.get("reschedule_date"),
            "reschedule_time": parsed.get("reschedule_time"),
            "clear_completed": bool(parsed.get("clear_completed", False)),
            "navigate_to": parsed.get("navigate_to", "chat"),
            "reset_draft": bool(parsed.get("reset_draft", False)),
        }
    except Exception:
        return _local_assistant_response(messages, draft, today_iso, task_context)
