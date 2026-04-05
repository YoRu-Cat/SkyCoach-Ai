import { useEffect, useRef, useState } from "react";
import type { ChatDraft, ChatMessage } from "@app-types/api";
import type { TaskStore } from "@hooks/useTaskStore";
import { chatAssistant } from "@services/api";

interface ChatPageProps {
  taskStore: TaskStore;
  onNavigate: (
    target: "dashboard" | "todo" | "timetable" | "planner" | "chat",
  ) => void;
}

const emptyDraft: ChatDraft = {
  task_title: null,
  date: null,
  time: null,
  notes: null,
};

const CHAT_STORAGE_KEY = "skycoach_chat_v1";

const starterMessage: ChatMessage = {
  role: "assistant",
  content:
    "I can run SkyCoach for you. Tell me a task and I will ask for day and time, then add it to Todo and Timetable after your confirmation.",
};

const loadChatState = (): { messages: ChatMessage[]; draft: ChatDraft } => {
  if (typeof window === "undefined") {
    return { messages: [starterMessage], draft: emptyDraft };
  }

  const raw = window.localStorage.getItem(CHAT_STORAGE_KEY);
  if (!raw) {
    return { messages: [starterMessage], draft: emptyDraft };
  }

  try {
    const parsed = JSON.parse(raw) as {
      messages?: ChatMessage[];
      draft?: ChatDraft;
    };

    const validMessages = (parsed.messages || []).filter(
      (message) =>
        (message.role === "user" || message.role === "assistant") &&
        typeof message.content === "string" &&
        message.content.trim().length > 0,
    );

    return {
      messages: validMessages.length ? validMessages : [starterMessage],
      draft: parsed.draft || emptyDraft,
    };
  } catch {
    return { messages: [starterMessage], draft: emptyDraft };
  }
};

export default function ChatPage({ taskStore, onNavigate }: ChatPageProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    () => loadChatState().messages,
  );
  const [draft, setDraft] = useState<ChatDraft>(() => loadChatState().draft);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    window.localStorage.setItem(
      CHAT_STORAGE_KEY,
      JSON.stringify({ messages, draft }),
    );
  }, [messages, draft]);

  useEffect(() => {
    if (!chatScrollRef.current) return;
    chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
  }, [messages, isLoading]);

  const startNewChat = () => {
    setMessages([starterMessage]);
    setDraft(emptyDraft);
    setInput("");
    window.localStorage.removeItem(CHAT_STORAGE_KEY);
  };

  const submitMessage = async () => {
    const content = input.trim();
    if (!content || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatAssistant(
        nextMessages,
        draft,
        taskStore.tasks.map((task) => ({
          id: task.id,
          title: task.title,
          completed: task.completed,
          scheduled_at: task.scheduledAt ?? null,
        })),
      );

      if (response.create_task && response.draft.task_title) {
        const createdId = taskStore.addTask(
          response.draft.task_title,
          response.draft.notes || undefined,
        );

        if (createdId && response.draft.date && response.draft.time) {
          taskStore.updateTask(createdId, {
            scheduledAt: `${response.draft.date}T${response.draft.time}:00`,
          });
        }
      }

      if (response.remove_task_id) {
        taskStore.removeTask(response.remove_task_id);
      }

      if (response.complete_task_id) {
        taskStore.updateTask(response.complete_task_id, { completed: true });
      }

      if (response.uncomplete_task_id) {
        taskStore.updateTask(response.uncomplete_task_id, { completed: false });
      }

      if (
        response.reschedule_task_id &&
        response.reschedule_date &&
        response.reschedule_time
      ) {
        taskStore.updateTask(response.reschedule_task_id, {
          scheduledAt: `${response.reschedule_date}T${response.reschedule_time}:00`,
        });
      }

      if (response.clear_completed) {
        taskStore.clearCompleted();
      }

      setDraft(response.reset_draft ? emptyDraft : response.draft);
      onNavigate(response.navigate_to);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: response.assistant_message },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "I could not process that right now. Please try again with task, day, and time.",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="card space-y-2">
        <h2 className="text-xl font-bold">SkyCoach Chat Control</h2>
        <p className="text-sm text-slate-400">
          Chat with the assistant to add, schedule, and navigate through the
          app.
        </p>
      </section>

      <section className="card space-y-3">
        <div className="flex items-center justify-between gap-3">
          <p className="text-xs text-slate-400">
            History is saved automatically.
          </p>
          <button
            type="button"
            onClick={startNewChat}
            disabled={isLoading}
            className="px-3 py-1.5 rounded-lg border border-slate-600 text-xs text-slate-200 hover:border-cyan-500/50 disabled:opacity-50">
            Start New Chat
          </button>
        </div>

        <div
          ref={chatScrollRef}
          className="h-[55vh] overflow-y-auto overscroll-contain space-y-3 pr-1"
          onWheelCapture={(event) => event.stopPropagation()}
          onTouchMoveCapture={(event) => event.stopPropagation()}>
          {messages.map((message, index) => (
            <div
              key={`${message.role}-${index}`}
              className={`p-3 rounded-lg border ${
                message.role === "user"
                  ? "bg-cyan-500/10 border-cyan-500/40 ml-8"
                  : "bg-slate-800/60 border-slate-700 mr-8"
              }`}>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">
                {message.role}
              </p>
              <p className="chat-readable text-sm text-slate-100 whitespace-pre-wrap">
                {message.content}
              </p>
            </div>
          ))}
          {isLoading ? (
            <p className="text-xs text-cyan-300">Assistant is thinking...</p>
          ) : null}
        </div>

        <div className="flex gap-2">
          <input
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                void submitMessage();
              }
            }}
            placeholder="Example: Add gym on Monday at 7 pm"
            className="chat-input-readable flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg"
          />
          <button
            type="button"
            onClick={() => void submitMessage()}
            disabled={isLoading}
            className="px-4 py-2 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-200 disabled:opacity-50">
            Send
          </button>
        </div>
      </section>
    </div>
  );
}
