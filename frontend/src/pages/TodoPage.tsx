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
}: TaskStore) {
  const [title, setTitle] = useState("");
  const [notes, setNotes] = useState("");

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
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Tasks</h3>
          <button
            type="button"
            onClick={clearCompleted}
            className="text-xs px-3 py-1.5 rounded-lg border border-slate-600 hover:border-cyan-500/50">
            Clear Completed
          </button>
        </div>

        {orderedTasks.length === 0 ? (
          <p className="text-slate-400">
            No tasks yet. Add your first task above.
          </p>
        ) : (
          orderedTasks.map((task) => (
            <div
              key={task.id}
              className="p-3 bg-slate-800/50 border border-slate-700 rounded-lg flex items-start justify-between gap-3">
              <div className="flex items-start gap-3">
                <button
                  type="button"
                  onClick={() =>
                    updateTask(task.id, { completed: !task.completed })
                  }
                  className={`mt-0.5 w-6 h-6 rounded-md border flex items-center justify-center ${
                    task.completed
                      ? "bg-emerald-500/30 border-emerald-300"
                      : "border-slate-500"
                  }`}>
                  {task.completed ? <Check className="w-4 h-4" /> : null}
                </button>
                <div className="space-y-2 w-full">
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-slate-500">
                      Event
                    </label>
                    <input
                      value={task.title}
                      onChange={(e) =>
                        updateTask(task.id, { title: e.target.value })
                      }
                      placeholder="Event title"
                      title={`Edit event title for ${task.title}`}
                      className={`mt-1 w-full rounded-md border bg-slate-900/60 px-3 py-2 text-sm outline-none transition-colors ${
                        task.completed
                          ? "border-slate-700 text-slate-500"
                          : "border-slate-700 text-slate-100 focus:border-cyan-500"
                      }`}
                    />
                  </div>
                  <div>
                    <label className="text-[11px] uppercase tracking-wide text-slate-500">
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
                      className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900/60 px-3 py-2 text-sm text-slate-100 outline-none transition-colors focus:border-cyan-500"
                    />
                  </div>
                  {task.scheduledAt ? (
                    <p className="text-xs text-cyan-300">
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
                className="p-2 rounded-lg border border-slate-700 hover:border-rose-400/70 text-rose-300">
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
