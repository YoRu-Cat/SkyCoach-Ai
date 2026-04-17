import { useEffect, useMemo, useRef, useState } from "react";
import type { TaskCategory, UserTask } from "@app-types/tasks";
import {
  reserveNextAvailableSlot,
  parseScheduledAt,
} from "@utils/taskScheduling";

const STORAGE_KEY = "skycoach_tasks_v1";

const byCreatedDesc = (a: UserTask, b: UserTask): number =>
  new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();

const loadTasks = (): UserTask[] => {
  if (typeof window === "undefined") {
    return [];
  }

  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) {
    return [];
  }

  try {
    const parsed = JSON.parse(raw) as UserTask[];
    return parsed
      .filter((task) => !!task.id && !!task.title)
      .sort(byCreatedDesc);
  } catch {
    return [];
  }
};

export const useTaskStore = () => {
  const [tasks, setTasks] = useState<UserTask[]>(() => loadTasks());
  const tasksRef = useRef<UserTask[]>(tasks);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }, [tasks]);

  useEffect(() => {
    tasksRef.current = tasks;
  }, [tasks]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const notifyDueTask = (task: UserTask) => {
      const title = task.title.trim() || "Scheduled task";
      const when = task.scheduledAt
        ? new Date(task.scheduledAt).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })
        : "now";

      if ("Notification" in window && Notification.permission === "granted") {
        new Notification("SkyCoach reminder", {
          body: `${title} is due ${when}`,
        });
      }

      try {
        const AudioContextCtor =
          window.AudioContext ||
          (
            window as typeof window & {
              webkitAudioContext?: typeof AudioContext;
            }
          ).webkitAudioContext;
        if (AudioContextCtor) {
          const audio = new AudioContextCtor();
          const oscillator = audio.createOscillator();
          const gain = audio.createGain();
          oscillator.type = "sine";
          oscillator.frequency.value = 880;
          gain.gain.value = 0.05;
          oscillator.connect(gain);
          gain.connect(audio.destination);
          oscillator.start();
          setTimeout(() => {
            oscillator.stop();
            audio.close().catch(() => undefined);
          }, 900);
        }
      } catch {
        // Ignore audio failures when the browser blocks autoplay.
      }
    };

    const requestNotificationPermission = async () => {
      if (!("Notification" in window)) return;
      if (Notification.permission === "default") {
        try {
          await Notification.requestPermission();
        } catch {
          // Ignore permission prompt failures.
        }
      }
    };

    const checkReminders = () => {
      const now = Date.now();
      const currentTasks = tasksRef.current;
      const dueTasks = currentTasks.filter((task) => {
        if (!task.scheduledAt || task.completed || task.remindedAt)
          return false;
        const dueTime = parseScheduledAt(task.scheduledAt);
        return !!dueTime && dueTime.getTime() <= now;
      });

      if (!dueTasks.length) return;

      void requestNotificationPermission();

      dueTasks.forEach((task) => notifyDueTask(task));

      setTasks((prev) =>
        prev.map((task) =>
          dueTasks.some((due) => due.id === task.id)
            ? { ...task, remindedAt: new Date().toISOString() }
            : task,
        ),
      );
    };

    checkReminders();
    const intervalId = window.setInterval(checkReminders, 30000);

    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        checkReminders();
      }
    };

    document.addEventListener("visibilitychange", onVisibilityChange);

    return () => {
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  const addTask = (
    title: string,
    notes?: string,
    scheduledAt?: string,
    category?: TaskCategory,
  ): string | null => {
    const trimmed = title.trim();
    if (!trimmed) return null;

    const resolvedScheduledAt = scheduledAt
      ? reserveNextAvailableSlot(tasksRef.current, scheduledAt)
      : undefined;

    const next: UserTask = {
      id: crypto.randomUUID(),
      title: trimmed,
      notes: notes?.trim() || undefined,
      createdAt: new Date().toISOString(),
      completed: false,
      category,
      scheduledAt: resolvedScheduledAt,
    };

    setTasks((prev) => [next, ...prev].sort(byCreatedDesc));
    return next.id;
  };

  const updateTask = (id: string, patch: Partial<UserTask>) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== id) return task;

        const nextPatch: Partial<UserTask> = { ...patch };

        if (Object.prototype.hasOwnProperty.call(nextPatch, "scheduledAt")) {
          nextPatch.scheduledAt = nextPatch.scheduledAt
            ? reserveNextAvailableSlot(prev, nextPatch.scheduledAt, id)
            : undefined;
          nextPatch.remindedAt = undefined;
        }

        if (Object.prototype.hasOwnProperty.call(nextPatch, "title")) {
          nextPatch.remindedAt = undefined;
        }

        return { ...task, ...nextPatch };
      }),
    );
  };

  const removeTask = (id: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  const clearCompleted = () => {
    setTasks((prev) => prev.filter((task) => !task.completed));
  };

  const stats = useMemo(() => {
    const completed = tasks.filter((task) => task.completed).length;
    const scheduled = tasks.filter((task) => !!task.scheduledAt).length;
    return {
      total: tasks.length,
      completed,
      pending: tasks.length - completed,
      scheduled,
    };
  }, [tasks]);

  return {
    tasks,
    stats,
    addTask,
    updateTask,
    removeTask,
    clearCompleted,
  };
};

export type TaskStore = ReturnType<typeof useTaskStore>;
