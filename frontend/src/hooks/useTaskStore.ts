import { useEffect, useMemo, useState } from "react";
import type { UserTask } from "@app-types/tasks";

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

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }, [tasks]);

  const addTask = (title: string, notes?: string) => {
    const trimmed = title.trim();
    if (!trimmed) return;

    const next: UserTask = {
      id: crypto.randomUUID(),
      title: trimmed,
      notes: notes?.trim() || undefined,
      createdAt: new Date().toISOString(),
      completed: false,
    };

    setTasks((prev) => [next, ...prev].sort(byCreatedDesc));
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
