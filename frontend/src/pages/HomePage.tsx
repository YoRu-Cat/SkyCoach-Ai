import { useEffect, useMemo, useRef, useState } from "react";
import {
  Bot,
  CalendarDays,
  ClipboardList,
  LayoutGrid,
  Send,
  Sparkles,
  TerminalSquare,
} from "lucide-react";
import type { ChatDraft, ChatMessage } from "@app-types/api";
import type { TaskStore } from "@hooks/useTaskStore";
import { chatAssistant, runBackendCliCommand } from "@services/api";

interface HomePageProps {
  taskStore: TaskStore;
  onNavigate: (
    target: "home" | "dashboard" | "todo" | "timetable" | "planner" | "chat",
  ) => void;
}

type CliLine = {
  type: "command" | "output" | "error";
  text: string;
  timestamp: string;
};

const formatCliTime = (iso: string): string => {
  const parsed = new Date(iso);
  if (Number.isNaN(parsed.getTime())) return "--:--:--";
  return parsed.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });
};

const getCliLevel = (line: CliLine): "CMD" | "INFO" | "WARN" | "ERROR" => {
  if (line.type === "command") return "CMD";
  if (line.type === "error") return "ERROR";
  if (/warn|warning/i.test(line.text)) return "WARN";
  return "INFO";
};

const CHAT_STORAGE_KEY = "skycoach_chat_v1";
const CLI_STORAGE_KEY = "skycoach_cli_v1";

const emptyDraft: ChatDraft = {
  task_title: null,
  date: null,
  time: null,
  notes: null,
};

const starterMessage: ChatMessage = {
  role: "assistant",
  content:
    "Welcome to SkyCoach Home. Chat with me or use the backend terminal panel for quick system commands.",
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

const loadCliState = (): CliLine[] => {
  if (typeof window === "undefined") {
    return [];
  }

  const raw = window.localStorage.getItem(CLI_STORAGE_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw) as CliLine[];
    return parsed.filter(
      (line) =>
        (line.type === "command" ||
          line.type === "output" ||
          line.type === "error") &&
        typeof line.text === "string" &&
        typeof line.timestamp === "string",
    );
  } catch {
    return [];
  }
};

export default function HomePage({ taskStore, onNavigate }: HomePageProps) {
  const [messages, setMessages] = useState<ChatMessage[]>(
    () => loadChatState().messages,
  );
  const [draft, setDraft] = useState<ChatDraft>(() => loadChatState().draft);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);

  const [cliInput, setCliInput] = useState("");
  const [cliLoading, setCliLoading] = useState(false);
  const [cliLines, setCliLines] = useState<CliLine[]>(() => loadCliState());
  const [cliSearch, setCliSearch] = useState("");

  const chatScrollRef = useRef<HTMLDivElement>(null);
  const cliScrollRef = useRef<HTMLDivElement>(null);

  const stats = useMemo(() => taskStore.stats, [taskStore.stats]);
  const filteredCliLines = useMemo(() => {
    const keyword = cliSearch.trim().toLowerCase();
    if (!keyword) return cliLines;
    return cliLines.filter((line) => line.text.toLowerCase().includes(keyword));
  }, [cliLines, cliSearch]);

  useEffect(() => {
    window.localStorage.setItem(
      CHAT_STORAGE_KEY,
      JSON.stringify({ messages, draft }),
    );
  }, [messages, draft]);

  useEffect(() => {
    window.localStorage.setItem(CLI_STORAGE_KEY, JSON.stringify(cliLines));
  }, [cliLines]);

  useEffect(() => {
    if (!chatScrollRef.current) return;
    chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
  }, [messages, chatLoading]);

  useEffect(() => {
    if (!cliScrollRef.current) return;
    cliScrollRef.current.scrollTop = cliScrollRef.current.scrollHeight;
  }, [cliLines, cliLoading]);

  const submitChat = async () => {
    const content = chatInput.trim();
    if (!content || chatLoading) return;

    const userMessage: ChatMessage = { role: "user", content };
    const nextMessages = [...messages, userMessage];
    setMessages(nextMessages);
    setChatInput("");
    setChatLoading(true);

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
            "Chat request failed. Please retry, or use backend terminal commands.",
        },
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  const runCommand = async (rawCommand?: string) => {
    const command = (rawCommand ?? cliInput).trim();
    if (!command || cliLoading) return;

    const now = new Date().toISOString();
    setCliLines((prev) => [
      ...prev,
      { type: "command", text: `$ ${command}`, timestamp: now },
    ]);
    setCliInput("");
    setCliLoading(true);

    try {
      const response = await runBackendCliCommand(command);
      setCliLines((prev) => [
        ...prev,
        {
          type: response.ok ? "output" : "error",
          text: response.output,
          timestamp: response.timestamp,
        },
      ]);
    } catch (error: unknown) {
      const message =
        typeof error === "object" &&
        error !== null &&
        "response" in error &&
        typeof (error as { response?: { data?: { detail?: string } } }).response
          ?.data?.detail === "string"
          ? (error as { response?: { data?: { detail?: string } } }).response!
              .data!.detail!
          : "Command failed. Try 'help'.";

      setCliLines((prev) => [
        ...prev,
        { type: "error", text: message, timestamp: new Date().toISOString() },
      ]);
    } finally {
      setCliLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="card border border-[#3e5c76]/55 bg-[#0b182a]/75 overflow-hidden">
        <div className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(circle_at_16%_20%,rgba(106,168,208,0.18),transparent_42%),radial-gradient(circle_at_86%_84%,rgba(62,92,118,0.2),transparent_48%)]" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <button
            type="button"
            onClick={() => onNavigate("todo")}
            className="rounded-xl border border-slate-600/70 bg-slate-900/35 p-3 text-left hover:border-cyan-400/50 transition-colors">
            <p className="text-xs text-slate-400">Tasks</p>
            <p className="text-lg font-semibold text-slate-100">
              {stats.total}
            </p>
          </button>
          <button
            type="button"
            onClick={() => onNavigate("timetable")}
            className="rounded-xl border border-slate-600/70 bg-slate-900/35 p-3 text-left hover:border-cyan-400/50 transition-colors">
            <p className="text-xs text-slate-400">Scheduled</p>
            <p className="text-lg font-semibold text-slate-100">
              {stats.scheduled}
            </p>
          </button>
          <button
            type="button"
            onClick={() => onNavigate("planner")}
            className="rounded-xl border border-slate-600/70 bg-slate-900/35 p-3 text-left hover:border-cyan-400/50 transition-colors">
            <p className="text-xs text-slate-400">Pending</p>
            <p className="text-lg font-semibold text-slate-100">
              {stats.pending}
            </p>
          </button>
          <button
            type="button"
            onClick={() => onNavigate("dashboard")}
            className="rounded-xl border border-slate-600/70 bg-slate-900/35 p-3 text-left hover:border-cyan-400/50 transition-colors">
            <p className="text-xs text-slate-400">Completed</p>
            <p className="text-lg font-semibold text-slate-100">
              {stats.completed}
            </p>
          </button>
        </div>
      </section>

      <section className="grid grid-cols-1 xl:grid-cols-5 gap-4">
        <div className="card xl:col-span-3 space-y-3 border border-cyan-900/35">
          <div className="flex items-center justify-between">
            <h2 className="text-base sm:text-lg font-semibold text-slate-100 flex items-center gap-2">
              <Bot className="w-4 h-4 text-cyan-300" />
              Home Chat Assistant
            </h2>
            <button
              type="button"
              onClick={() => onNavigate("chat")}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-600 text-slate-300 hover:border-cyan-500/50">
              Open Full Chat
            </button>
          </div>

          <div
            ref={chatScrollRef}
            className="h-[46vh] overflow-y-auto overscroll-contain space-y-3 pr-1"
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
            {chatLoading ? (
              <p className="text-xs text-cyan-300">Assistant is thinking...</p>
            ) : null}
          </div>

          <div className="flex gap-2">
            <input
              value={chatInput}
              onChange={(event) => setChatInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void submitChat();
                }
              }}
              placeholder="Ask: add workout tomorrow at 7 pm"
              className="chat-input-readable flex-1 px-3 py-2 bg-[var(--color-glass-bg)] border border-slate-600 rounded-lg"
            />
            <button
              type="button"
              onClick={() => void submitChat()}
              disabled={chatLoading}
              aria-label="Send chat message"
              title="Send chat message"
              className="px-4 py-2 rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-200 disabled:opacity-50">
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="card xl:col-span-2 space-y-3 border border-emerald-900/35">
          <div className="backend-logs-shell rounded-xl border border-slate-700/80 bg-[#060b14]/95 overflow-hidden shadow-[0_12px_30px_rgba(2,6,23,0.55)]">
            <div className="backend-logs-head flex items-center justify-between gap-2 border-b border-slate-800/90 bg-[#0a111d] px-3 py-2">
              <div className="flex items-center gap-2 text-slate-200">
                <TerminalSquare className="w-4 h-4 text-emerald-300" />
                <p className="text-xs font-semibold tracking-wide uppercase">
                  Backend Logs
                </p>
              </div>
              <p className="text-[11px] text-slate-400">SkyCoach-Ai</p>
            </div>

            <div className="backend-logs-toolbar grid grid-cols-12 gap-2 border-b border-slate-800/90 bg-[#070d18] px-3 py-2">
              <button
                type="button"
                className="backend-logs-filter col-span-3 rounded-md border border-slate-700 bg-[#0a1220] px-2 py-1 text-left text-[11px] text-slate-200">
                All logs
              </button>
              <input
                value={cliSearch}
                onChange={(event) => setCliSearch(event.target.value)}
                placeholder="Search logs"
                className="backend-logs-search col-span-6 rounded-md border border-slate-700 bg-[#0a1220] px-2 py-1 text-[11px] text-slate-200 placeholder:text-slate-500"
              />
              <button
                type="button"
                className="backend-logs-range col-span-3 rounded-md border border-slate-700 bg-[#0a1220] px-2 py-1 text-[11px] text-slate-300">
                Last hour
              </button>
            </div>

            <div
              ref={cliScrollRef}
              className="backend-logs-stream h-[33vh] overflow-y-auto bg-[#050a12] font-mono text-xs"
              onWheelCapture={(event) => event.stopPropagation()}
              onTouchMoveCapture={(event) => event.stopPropagation()}>
              {filteredCliLines.length === 0 ? (
                <p className="backend-logs-empty px-3 py-3 text-slate-500">
                  No logs yet. Run help.
                </p>
              ) : (
                filteredCliLines.map((line, index) => {
                  const level = getCliLevel(line);
                  const levelClass =
                    level === "ERROR"
                      ? "text-rose-300"
                      : level === "WARN"
                        ? "text-amber-300"
                        : level === "CMD"
                          ? "text-cyan-300"
                          : "text-emerald-300";

                  return (
                    <div
                      key={`${line.timestamp}-${index}`}
                      className="backend-logs-row grid grid-cols-12 gap-2 border-b border-slate-900/70 px-3 py-1.5 hover:bg-[#08101d]">
                      <p className="backend-logs-time col-span-3 text-[11px] text-slate-500">
                        {formatCliTime(line.timestamp)}
                      </p>
                      <p
                        className={`backend-logs-level col-span-2 text-[11px] font-semibold ${levelClass}`}>
                        {level}
                      </p>
                      <p className="backend-logs-message col-span-7 text-[11px] text-slate-300 whitespace-pre-wrap break-words">
                        {line.text}
                      </p>
                    </div>
                  );
                })
              )}
              {cliLoading ? (
                <p className="backend-logs-running px-3 py-2 text-[11px] text-slate-500">
                  Running command...
                </p>
              ) : null}
            </div>
          </div>

          <div className="flex flex-wrap gap-2">
            {[
              "help",
              "health",
              "version",
              "time",
              "weather Tokyo",
              "analyze go running in rain",
            ].map((cmd) => (
              <button
                key={cmd}
                type="button"
                onClick={() => void runCommand(cmd)}
                className="backend-logs-chip text-xs px-2 py-1 rounded-md border border-slate-600/80 text-slate-300 bg-slate-900/40 hover:border-emerald-400/55">
                {cmd}
              </button>
            ))}
          </div>

          <div className="flex gap-2">
            <input
              value={cliInput}
              onChange={(event) => setCliInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  event.preventDefault();
                  void runCommand();
                }
              }}
              placeholder="Type backend command..."
              className="backend-logs-input flex-1 px-3 py-2 rounded-lg border border-slate-600 bg-[#0a1220] font-mono text-sm"
            />
            <button
              type="button"
              onClick={() => void runCommand()}
              disabled={cliLoading}
              className="backend-logs-run px-3 py-2 rounded-lg border border-emerald-400/70 text-emerald-200 bg-emerald-500/15 disabled:opacity-50">
              Run
            </button>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <button
          type="button"
          onClick={() => onNavigate("dashboard")}
          className="card p-4 text-left border border-slate-700 hover:border-cyan-500/50 transition-colors">
          <p className="text-slate-200 font-semibold flex items-center gap-2">
            <LayoutGrid className="w-4 h-4" />
            Core Analysis
          </p>
          <p className="text-sm text-slate-400 mt-1">
            Analyze activities against live weather and score fitness.
          </p>
        </button>
        <button
          type="button"
          onClick={() => onNavigate("todo")}
          className="card p-4 text-left border border-slate-700 hover:border-cyan-500/50 transition-colors">
          <p className="text-slate-200 font-semibold flex items-center gap-2">
            <ClipboardList className="w-4 h-4" />
            Todo Control
          </p>
          <p className="text-sm text-slate-400 mt-1">
            Add, organize, and complete your execution queue.
          </p>
        </button>
        <button
          type="button"
          onClick={() => onNavigate("timetable")}
          className="card p-4 text-left border border-slate-700 hover:border-cyan-500/50 transition-colors">
          <p className="text-slate-200 font-semibold flex items-center gap-2">
            <CalendarDays className="w-4 h-4" />
            Timetable Grid
          </p>
          <p className="text-sm text-slate-400 mt-1">
            Lock your week and schedule each task with date and time.
          </p>
        </button>
      </section>

      <section className="card border border-amber-900/35 bg-slate-900/35">
        <p className="text-sm text-slate-300 flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-amber-300" />
          Home combines chat + backend terminal + quick navigation so your full
          stack workflow starts in one place.
        </p>
      </section>
    </div>
  );
}
