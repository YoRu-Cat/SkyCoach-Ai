import { useMemo } from "react";
import type { TaskStore } from "@hooks/useTaskStore";

const formatDate = (date: Date) => date.toISOString().slice(0, 10);

const getDateBounds = () => {
  const now = new Date();
  const max = new Date();
  max.setDate(now.getDate() + 6);
  return {
    minDate: formatDate(now),
    maxDate: formatDate(max),
  };
};

export default function TimetablePage({ tasks, updateTask }: TaskStore) {
  const { minDate, maxDate } = useMemo(() => getDateBounds(), []);

  const sorted = useMemo(
    () =>
      [...tasks].sort((a, b) => {
        if (!a.scheduledAt && !b.scheduledAt) return 0;
        if (!a.scheduledAt) return 1;
        if (!b.scheduledAt) return -1;
        return (
          new Date(a.scheduledAt).getTime() - new Date(b.scheduledAt).getTime()
        );
      }),
    [tasks],
  );

  return (
    <div className="space-y-6">
      <section className="card">
        <h2 className="text-xl font-bold mb-2">1-Week Timetable</h2>
        <p className="text-slate-400 text-sm">
          Schedule each task within the next 7 days. Date range is locked from
          today to one week ahead.
        </p>
      </section>

      <section className="card space-y-3">
        {sorted.length === 0 ? (
          <p className="text-slate-400">Create tasks first in Todo List.</p>
        ) : (
          sorted.map((task) => {
            const currentDate = task.scheduledAt
              ? task.scheduledAt.slice(0, 10)
              : "";
            const currentTime = task.scheduledAt
              ? task.scheduledAt.slice(11, 16)
              : "";

            return (
              <div
                key={task.id}
                className="p-3 bg-slate-800/50 border border-slate-700 rounded-lg space-y-2">
                <p className="font-medium">{task.title}</p>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <input
                    type="date"
                    min={minDate}
                    max={maxDate}
                    value={currentDate}
                    onChange={(e) => {
                      const date = e.target.value;
                      if (!date) {
                        updateTask(task.id, { scheduledAt: undefined });
                        return;
                      }
                      const time = currentTime || "09:00";
                      updateTask(task.id, {
                        scheduledAt: `${date}T${time}:00`,
                      });
                    }}
                    className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg"
                  />
                  <input
                    type="time"
                    value={currentTime}
                    onChange={(e) => {
                      const time = e.target.value;
                      if (!currentDate) return;
                      updateTask(task.id, {
                        scheduledAt: `${currentDate}T${time}:00`,
                      });
                    }}
                    className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() =>
                      updateTask(task.id, { scheduledAt: undefined })
                    }
                    className="px-3 py-2 border border-slate-700 rounded-lg text-sm hover:border-cyan-500/50">
                    Clear Slot
                  </button>
                </div>
              </div>
            );
          })
        )}
      </section>
    </div>
  );
}
