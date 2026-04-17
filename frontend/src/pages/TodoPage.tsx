import { useMemo, useState } from "react";
import { Check, Plus, Trash2 } from "lucide-react";
import type { TaskStore } from "@hooks/useTaskStore";

export default function TodoPage({
  tasks,
  stats,
  addTask,
  updateTask,
  removeTask,
  clearCompleted,
  notificationPermission,
  enableNotifications,
  testReminder,
}: TaskStore) {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");
  const [testingPreset, setTestingPreset] = useState<
    "bell" | "chime" | "alarm"
  >("bell");
  const [reminderStatus, setReminderStatus] = useState<string>("");

  const orderedTasks = useMemo(
    () => [...tasks].sort((a, b) => Number(a.completed) - Number(b.completed)),
    [tasks],
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
      <section className="card border border-[#7d4fc7]/45 bg-[linear-gradient(180deg,rgba(34,1,53,0.72)_0%,rgba(17,0,28,0.78)_100%)] shadow-[0_14px_30px_rgba(0,0,0,0.28)]">
        <h2 className="text-xl font-bold mb-4 text-[#f2ddff]">Todo List</h2>
        <form onSubmit={onSubmit} className="space-y-3">
          <input
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Add a task..."
            className="w-full px-4 py-3 rounded-lg bg-[rgba(23,4,36,0.9)] border border-[#6f45b5]/65 text-[#f3e6ff] placeholder:text-[#ad88da] focus:border-[#c29df7] focus:outline-none"
          />
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Optional notes"
            className="w-full px-4 py-3 rounded-lg bg-[rgba(23,4,36,0.9)] border border-[#6f45b5]/65 text-[#f3e6ff] placeholder:text-[#ad88da] focus:border-[#c29df7] focus:outline-none"
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
        <div className="card border border-[#6f45b5]/55 bg-[rgba(31,4,47,0.82)]">
          <p className="text-[#b798df] text-xs">Total</p>
          <p className="text-2xl font-bold text-[#f1dcff]">{stats.total}</p>
        </div>
        <div className="card border border-[#6f45b5]/55 bg-[rgba(31,4,47,0.82)]">
          <p className="text-[#b798df] text-xs">Pending</p>
          <p className="text-2xl font-bold text-[#f1dcff]">{stats.pending}</p>
        </div>
        <div className="card border border-[#6f45b5]/55 bg-[rgba(31,4,47,0.82)]">
          <p className="text-[#b798df] text-xs">Completed</p>
          <p className="text-2xl font-bold text-[#f1dcff]">{stats.completed}</p>
        </div>
        <div className="card border border-[#6f45b5]/55 bg-[rgba(31,4,47,0.82)]">
          <p className="text-[#b798df] text-xs">Scheduled</p>
          <p className="text-2xl font-bold text-[#f1dcff]">{stats.scheduled}</p>
        </div>
      </section>

      <section className="card space-y-3 border border-[#7d4fc7]/45 bg-[rgba(28,2,44,0.86)]">
        <h3 className="text-lg font-semibold text-[#f1dcff]">
          Reminder Settings
        </h3>
        <p className="text-sm text-[#b798df]">
          Notification status:{" "}
          <span className="text-[#ecd6ff]">{notificationPermission}</span>
        </p>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleEnableNotifications}
            className="px-3 py-2 text-xs rounded-lg border border-[#c29df7]/70 bg-[rgba(145,83,219,0.38)] text-[#f5e8ff] hover:bg-[rgba(168,107,239,0.52)] transition-colors">
            Enable Notifications
          </button>
          <select
            value={testingPreset}
            onChange={(e) =>
              setTestingPreset(e.target.value as "bell" | "chime" | "alarm")
            }
            aria-label="Reminder ringtone preset"
            title="Reminder ringtone preset"
            className="px-3 py-2 text-xs rounded-lg border border-[#7d4fc7]/65 bg-[rgba(21,2,34,0.9)] text-[#f1dcff] focus:border-[#c29df7] focus:outline-none">
            <option value="bell">Bell</option>
            <option value="chime">Chime</option>
            <option value="alarm">Alarm</option>
          </select>
          <button
            type="button"
            onClick={handleTestReminder}
            className="px-3 py-2 text-xs rounded-lg border border-[#a56ae8]/70 bg-[rgba(127,63,209,0.35)] text-[#f5e9ff] hover:bg-[rgba(145,83,219,0.5)] transition-colors">
            Test Reminder Sound
          </button>
        </div>
        {reminderStatus ? (
          <p className="text-xs text-[#d7b7ff]">{reminderStatus}</p>
        ) : null}
      </section>

      <section className="card space-y-3 border border-[#7d4fc7]/45 bg-[rgba(28,2,44,0.86)]">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-[#f1dcff]">Tasks</h3>
          <button
            type="button"
            onClick={clearCompleted}
            className="text-xs px-3 py-1.5 rounded-lg border border-[#7d4fc7]/65 text-[#e9d2ff] hover:border-[#bf97f4] hover:bg-[rgba(127,63,209,0.16)] transition-colors">
            Clear Completed
          </button>
        </div>

        {orderedTasks.length === 0 ? (
          <p className="text-[#b798df]">
            No tasks yet. Add your first task above.
          </p>
        ) : (
          orderedTasks.map((task) => (
            <div
              key={task.id}
              className="p-4 bg-[linear-gradient(180deg,rgba(34,1,53,0.76)_0%,rgba(17,0,28,0.82)_100%)] border border-[#6f45b5]/55 rounded-xl flex items-start justify-between gap-3 shadow-[inset_0_0_0_1px_rgba(185,126,241,0.14)]">
              <div className="flex items-start gap-3">
                <button
                  type="button"
                  onClick={() =>
                    updateTask(task.id, { completed: !task.completed })
                  }
                  className={`mt-0.5 w-6 h-6 rounded-md border flex items-center justify-center ${
                    task.completed
                      ? "bg-[rgba(145,83,219,0.55)] border-[#d5b1ff]"
                      : "border-[#8a5fcb] bg-[rgba(22,3,34,0.8)]"
                  }`}>
                  {task.completed ? <Check className="w-4 h-4" /> : null}
                </button>
                <div className="space-y-2 w-full">
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-[#b798df]">
                      Event
                    </label>
                    <input
                      value={task.title}
                      onChange={(e) =>
                        updateTask(task.id, { title: e.target.value })
                      }
                      placeholder="Event title"
                      title={`Edit event title for ${task.title}`}
                      className={`mt-1 w-full rounded-md border bg-[rgba(21,2,34,0.92)] px-3 py-2 text-sm outline-none transition-colors ${
                        task.completed
                          ? "border-[#5e3b91] text-[#9c82bf]"
                          : "border-[#7d4fc7]/65 text-[#f3e6ff] focus:border-[#c29df7]"
                      }`}
                    />
                  </div>
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-[#b798df]">
                      Notes
                    </label>
                    <input
                      value={task.notes || ""}
                      onChange={(e) =>
                        updateTask(task.id, {
                          notes: e.target.value || undefined,
                        })
                      }
                      placeholder="Optional notes"
                      className="mt-1 w-full rounded-md border border-[#7d4fc7]/65 bg-[rgba(21,2,34,0.92)] px-3 py-2 text-sm text-[#f3e6ff] outline-none transition-colors focus:border-[#c29df7]"
                    />
                  </div>
                  {task.scheduledAt ? (
                    <p className="text-xs text-[#d7b7ff]">
                      Scheduled: {new Date(task.scheduledAt).toLocaleString()}
                    </p>
                  ) : null}
                </div>
              </div>
              <button
                type="button"
                onClick={() => removeTask(task.id)}
                aria-label={`Delete task ${task.title}`}
                title={`Delete task ${task.title}`}
                className="p-2 rounded-lg border border-[#7d4fc7]/65 text-[#d7b7ff] hover:border-[#d8b6ff] hover:bg-[rgba(127,63,209,0.16)] transition-colors">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
