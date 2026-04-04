import { useState } from "react";
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

export default function ChatPage({ taskStore, onNavigate }: ChatPageProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "I can run SkyCoach for you. Tell me a task and I will ask for day and time, then add it to Todo and Timetable after your confirmation.",
    },
  ]);
  const [draft, setDraft] = useState<ChatDraft>(emptyDraft);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const submitMessage = async () => {
    const content = input.trim();
    if (!content || isLoading) return;

    const userMessage: ChatMessage = { role: "user", content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setInput("");
    setIsLoading(true);

    try {
      const response = await chatAssistant(nextMessages, draft);

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
        <div className="max-h-[55vh] overflow-y-auto space-y-3 pr-1">
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
              <p className="text-sm text-slate-100 whitespace-pre-wrap">
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
            className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg"
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
