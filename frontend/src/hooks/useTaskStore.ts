import { useEffect, useMemo, useState } from "react";
import type { TaskCategory, UserTask } from "@app-types/tasks";
import { analyzeTask } from "@services/api";

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

  const relabelSignature = useMemo(
    () =>
      tasks
        .map((task) => `${task.id}:${task.title}`)
        .sort()
        .join("|"),
    [tasks],
  );

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }, [tasks]);

  useEffect(() => {
    if (!tasks.length) return;

    let cancelled = false;

    const relabelTasks = async () => {
      const updates = await Promise.all(
        tasks.map(async (task) => {
          try {
            const result = await analyzeTask(task.title, true);
            const normalized = result.classification.toLowerCase();
            const category: TaskCategory =
              normalized === "outdoor" ? "outdoor" : "indoor";

            if (task.category === category) {
              return null;
            }

            return { id: task.id, category };
          } catch {
            return null;
          }
        }),
      );

      if (cancelled) return;

      const updateMap = new Map(
        updates
          .filter((entry): entry is { id: string; category: TaskCategory } =>
            Boolean(entry),
          )
          .map((entry) => [entry.id, entry.category]),
      );

      if (!updateMap.size) {
        return;
      }

      setTasks((prev) =>
        prev
          .map((task) => {
            const category = updateMap.get(task.id);
            return category ? { ...task, category } : task;
          })
          .sort(byCreatedDesc),
      );
    };

    void relabelTasks();

    return () => {
      cancelled = true;
    };
  }, [relabelSignature]);

  const addTask = (title: string, notes?: string): string | null => {
    const trimmed = title.trim();
    if (!trimmed) return null;

    const next: UserTask = {
      id: crypto.randomUUID(),
      title: trimmed,
      notes: notes?.trim() || undefined,
      createdAt: new Date().toISOString(),
      completed: false,
    };

    setTasks((prev) => [next, ...prev].sort(byCreatedDesc));
    return next.id;
  };

  const updateTask = (id: string, patch: Partial<UserTask>) => {
    setTasks((prev) =>
      prev.map((task) => (task.id === id ? { ...task, ...patch } : task)),
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
