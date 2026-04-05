from services.chat_assistant import chat_assistant_reply


def test_chat_assistant_uses_local_controller_for_remove_when_openai_key_exists(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    result = chat_assistant_reply(
        messages=[{"role": "user", "content": "remove gym"}],
        draft={"task_title": None, "date": None, "time": None, "notes": None},
        task_context=[
            {"id": "task-1", "title": "gym", "completed": False, "scheduled_at": None}
        ],
        use_openai=True,
    )

    assert result["remove_task_id"] == "task-1"
    assert result["assistant_message"] == "Removed 'gym' from your Todo and Timetable."


def test_chat_assistant_uses_local_controller_for_confirm_add_when_openai_key_exists(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    result = chat_assistant_reply(
        messages=[
            {"role": "user", "content": "add gym on monday at 7 pm"},
            {
                "role": "assistant",
                "content": "I understood: add 'gym' on 2026-04-06 at 19:00. Should I create it now?",
            },
            {"role": "user", "content": "yes"},
        ],
        draft={"task_title": "gym", "date": "2026-04-06", "time": "19:00", "notes": None},
        task_context=[],
        use_openai=True,
    )

    assert result["create_task"] is True
    assert result["reset_draft"] is True
    assert result["navigate_to"] == "timetable"