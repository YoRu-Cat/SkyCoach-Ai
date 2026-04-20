import { useEffect, useMemo, useState } from "react";
import { Check, Plus, Trash2 } from "lucide-react";
import type { TaskStore } from "@hooks/useTaskStore";

type ThemeMode = "dark" | "light";
const TASKS_PER_PAGE = 5;

export default function TodoPage({
  themeMode = "dark",
  tasks,
  stats,
  addTask,
  updateTask,
  removeTask,
  clearCompleted,
  notificationPermission,
  pendingDueTaskIds,
  enableNotifications,
  testReminder,
  completeDueTask,
  rescheduleDueTask,
}: TaskStore & { themeMode?: ThemeMode }) {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [testingPreset, setTestingPreset] = useState<
    "bell" | "chime" | "alarm"
  >("bell");
  const [reminderStatus, setReminderStatus] = useState<string>("");
  const [currentPage, setCurrentPage] = useState(1);

  const orderedTasks = useMemo(
    () => [...tasks].sort((a, b) => Number(a.completed) - Number(b.completed)),
    [tasks],
  );

  const taskById = useMemo(
    () => new Map(tasks.map((task) => [task.id, task])),
    [tasks],
  );

  const totalPages = Math.max(
    1,
    Math.ceil(orderedTasks.length / TASKS_PER_PAGE),
  );

  useEffect(() => {
    setCurrentPage((prev) => Math.min(prev, totalPages));
  }, [totalPages]);

  const pagedTasks = useMemo(() => {
    const start = (currentPage - 1) * TASKS_PER_PAGE;
    return orderedTasks.slice(start, start + TASKS_PER_PAGE);
  }, [orderedTasks, currentPage]);

  const duePromptTasks = useMemo(
    () =>
      pendingDueTaskIds
        .map((id) => taskById.get(id))
        .filter((task): task is NonNullable<typeof task> => Boolean(task)),
    [pendingDueTaskIds, taskById],
  );

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    addTask(title, notes);
    setTitle("");
    setNotes("");
  };

  const handleEnableNotifications = async () => {
    const permission = await enableNotifications();
    if (permission === "granted") {
      setReminderStatus("Notifications enabled.");
      return;
    }
    if (permission === "denied") {
      setReminderStatus("Notifications blocked in browser settings.");
      return;
    }
    setReminderStatus("Notifications unavailable in this environment.");
  };

  const handleTestReminder = async () => {
    const result = await testReminder(testingPreset);
    if (result.didPlay) {
      setReminderStatus(`Played ${testingPreset} ringtone test.`);
      return;
    }
    setReminderStatus(
      result.permission === "granted"
        ? "Ringtone blocked until you interact with the page."
        : "Enable notifications first, then test ringtone.",
    );
  };

  return (
    <div className="space-y-6">
      <section className="card">
        <h2 className="text-xl font-bold mb-4">Todo List</h2>
        <form onSubmit={onSubmit} className="space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Add a task..."
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
          />
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional notes"
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100"
            rows={3}
          />
          <button
            type="submit"
            className="btn btn-primary flex items-center gap-2">
            <Plus className="w-4 h-4" />
            Add Task
          </button>
        </form>
      </section>

      <section className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="card">
          <p className="text-slate-400 text-xs">Total</p>
          <p className="text-2xl font-bold">{stats.total}</p>
        </div>
        <div className="card">
          <p className="text-slate-400 text-xs">Pending</p>
          <p className="text-2xl font-bold">{stats.pending}</p>
        </div>
        <div className="card">
          <p className="text-slate-400 text-xs">Completed</p>
          <p className="text-2xl font-bold">{stats.completed}</p>
        </div>
        <div className="card">
          <p className="text-slate-400 text-xs">Scheduled</p>
          <p className="text-2xl font-bold">{stats.scheduled}</p>
        </div>
      </section>

      <section className="card space-y-3">
        <h3 className="text-lg font-semibold">Reminder Settings</h3>
        <p className="text-sm text-slate-400">
          Notification status:{" "}
          <span className="text-slate-200">{notificationPermission}</span>
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleEnableNotifications}
            className="px-3 py-2 text-xs rounded-lg border border-violet-300/70 bg-violet-500/30 text-violet-50 hover:bg-violet-500/50 transition-colors">
            Enable Notifications
          </button>
          <select
            value={testingPreset}
            onChange={(e) =>
              setTestingPreset(e.target.value as "bell" | "chime" | "alarm")
            }
            aria-label="Reminder ringtone preset"
            title="Reminder ringtone preset"
            className="px-3 py-2 text-xs rounded-lg border border-slate-600 bg-slate-900 text-slate-100 focus:border-violet-300 focus:outline-none">
            <option value="bell">Bell</option>
            <option value="chime">Chime</option>
            <option value="alarm">Alarm</option>
          </select>
          <button
            type="button"
            onClick={handleTestReminder}
            className="px-3 py-2 text-xs rounded-lg border border-violet-300/70 bg-violet-500/30 text-violet-50 hover:bg-violet-500/50 transition-colors">
            Test Reminder Sound
          </button>
        </div>
        {reminderStatus ? (
          <p className="text-xs text-slate-300">{reminderStatus}</p>
        ) : null}
      </section>

      {duePromptTasks.length > 0 ? (
        <section className="card space-y-3 border border-violet-300/55 bg-violet-500/10">
          <h3 className="text-lg font-semibold text-slate-100">
            Activity Check
          </h3>
          <p className="text-sm text-slate-300">
            The scheduled time has passed. Did you complete the activity?
          </p>
          <div className="space-y-2">
            {duePromptTasks.map((task) => (
              <div
                key={task.id}
                className="rounded-lg border border-slate-700 bg-slate-800/50 px-3 py-3 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
                <div>
                  <p className="text-sm font-medium text-slate-100">
                    {task.title}
                  </p>
                  {task.scheduledAt ? (
                    <p className="text-xs text-slate-400">
                      Scheduled: {new Date(task.scheduledAt).toLocaleString()}
                    </p>
                  ) : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => completeDueTask(task.id)}
                    className="px-3 py-1.5 text-xs rounded-lg border border-violet-300/75 bg-violet-500/40 text-violet-50 hover:bg-violet-500/55 transition-colors">
                    Yes, completed
                  </button>
                  <button
                    type="button"
                    onClick={() => rescheduleDueTask(task.id)}
                    className="px-3 py-1.5 text-xs rounded-lg border border-violet-300/75 bg-violet-500/25 text-violet-100 hover:bg-violet-500/40 transition-colors">
                    No, reschedule
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>
      ) : null}

      <section className="card space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Tasks</h3>
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">
              Page {currentPage} of {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              disabled={currentPage === 1}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-600 hover:border-violet-300/60 transition-colors disabled:opacity-45 disabled:cursor-not-allowed">
              Prev 5
            </button>
            <button
              type="button"
              onClick={() =>
                setCurrentPage((prev) => Math.min(totalPages, prev + 1))
              }
              disabled={currentPage === totalPages}
              className="text-xs px-2.5 py-1.5 rounded-lg border border-slate-600 hover:border-violet-300/60 transition-colors disabled:opacity-45 disabled:cursor-not-allowed">
              Next 5
            </button>
            <button
              type="button"
              onClick={clearCompleted}
              className="text-xs px-3 py-1.5 rounded-lg border border-slate-600 hover:border-violet-300/60 transition-colors">
              Clear Completed
            </button>
          </div>
        </div>

        {orderedTasks.length === 0 ? (
          <p className="text-slate-400">
            No tasks yet. Add your first task above.
          </p>
        ) : (
          pagedTasks.map((task) => (
            <div
              key={task.id}
              className="p-3 bg-slate-800/50 border border-slate-700 rounded-lg space-y-3">
              <div className="flex items-start gap-3">
                <button
                  type="button"
                  onClick={() =>
                    updateTask(task.id, { completed: !task.completed })
                  }
                  aria-label={
                    task.completed
                      ? `Mark task ${task.title} as not completed`
                      : `Mark task ${task.title} as completed`
                  }
                  className={`mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-md border transition-colors focus:outline-none focus:ring-2 focus:ring-violet-300 focus:ring-offset-2 focus:ring-offset-transparent ${
                    task.completed
                      ? themeMode === "light"
                        ? "border-[#7c45b8] bg-[#8a59d5] text-white shadow-[0_0_0_1px_rgba(124,69,184,0.3),0_0_10px_rgba(138,89,213,0.2)]"
                        : "border-violet-200 bg-violet-500/80 text-white shadow-[0_0_0_1px_rgba(217,70,239,0.35),0_0_14px_rgba(168,85,247,0.25)]"
                      : themeMode === "light"
                        ? "border-[#9d77e4] bg-[#f1e9fb] text-[#6a47a8] shadow-[0_0_0_1px_rgba(157,119,228,0.24)] hover:bg-[#e8dbf8] hover:border-[#8a59d5]"
                        : "border-violet-200/80 bg-[rgba(62,16,101,0.96)] text-violet-100 shadow-[0_0_0_1px_rgba(168,85,247,0.18)] hover:bg-violet-500/25 hover:border-violet-100"
                  }`}>
                  {task.completed ? <Check className="h-4 w-4" /> : null}
                </button>
                <div className="space-y-2 w-full">
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-slate-500">
                      Event
                    </label>
                    <textarea
                      value={task.title}
                      onChange={(e) =>
                        updateTask(task.id, { title: e.target.value })
                      }
                      placeholder="Event title"
                      title={`Edit event title for ${task.title}`}
                      rows={2}
                      className={`mt-1 w-full resize-y rounded-md border bg-[var(--color-glass-bg)] px-3 py-2 text-sm outline-none transition-colors ${
                        task.completed
                          ? "border-slate-700 text-slate-500"
                          : "border-slate-700 text-slate-100 focus:border-violet-300"
                      }`}
                    />
                  </div>
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-slate-500">
                      Notes
                    </label>
                    <textarea
                      value={task.notes || ""}
                      onChange={(e) =>
                        updateTask(task.id, {
                          notes: e.target.value || undefined,
                        })
                      }
                      placeholder="Optional notes"
                      rows={3}
                      className="mt-1 w-full resize-y rounded-md border border-slate-700 bg-[var(--color-glass-bg)] px-3 py-2 text-sm text-slate-100 outline-none transition-colors focus:border-violet-300"
                    />
                  </div>
                  {task.scheduledAt ? (
                    <p className="text-xs text-violet-200">
                      Scheduled: {new Date(task.scheduledAt).toLocaleString()}
                    </p>
                  ) : null}
                </div>
                <button
                  type="button"
                  onClick={() => removeTask(task.id)}
                  aria-label={`Delete task ${task.title}`}
                  title={`Delete task ${task.title}`}
                  className="p-2 rounded-lg border border-slate-700 hover:border-violet-300/70 text-violet-200 transition-colors">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
