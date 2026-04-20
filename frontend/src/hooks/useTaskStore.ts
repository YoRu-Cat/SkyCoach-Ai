import { useEffect, useMemo, useRef, useState } from "react";
import type { TaskCategory, UserTask } from "@app-types/tasks";
import {
  reserveNextAvailableSlot,
  parseScheduledAt,
  formatScheduledDate,
  formatScheduledTime,
} from "@utils/taskScheduling";

const STORAGE_KEY = "skycoach_tasks_v1";
const SAFETY_POLL_MS = 10_000;
const MAX_TIMER_DELAY_MS = 2_147_483_000;

export type RingtonePreset = "bell" | "chime" | "alarm";

const getAudioContext = () => {
  if (typeof window === "undefined") return null;
  const AudioContextCtor =
    window.AudioContext ||
    (
      window as typeof window & {
        webkitAudioContext?: typeof AudioContext;
      }
    ).webkitAudioContext;
  if (!AudioContextCtor) return null;
  return new AudioContextCtor();
};

const scheduleBellNote = (
  audio: AudioContext,
  at: number,
  frequency: number,
  duration: number,
  volume: number,
) => {
  const partials = [1, 2.01, 2.98];
  partials.forEach((partial, index) => {
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    oscillator.type = "sine";
    oscillator.frequency.setValueAtTime(frequency * partial, at);

    const weightedVolume =
      volume * (index === 0 ? 1 : index === 1 ? 0.35 : 0.2);
    gain.gain.setValueAtTime(0.0001, at);
    gain.gain.linearRampToValueAtTime(weightedVolume, at + 0.02);
    gain.gain.exponentialRampToValueAtTime(0.0001, at + duration);

    oscillator.connect(gain);
    gain.connect(audio.destination);
    oscillator.start(at);
    oscillator.stop(at + duration + 0.04);
  });
};

const playRingtonePreset = (preset: RingtonePreset) => {
  try {
    const audio = getAudioContext();
    if (!audio) return false;

    const now = audio.currentTime + 0.05;
    const patterns: Record<
      RingtonePreset,
      {
        tones: number[];
        gap: number;
        repeats: number;
        duration: number;
        volume: number;
      }
    > = {
      bell: {
        tones: [1046.5, 1318.5, 1568],
        gap: 0.35,
        repeats: 3,
        duration: 0.9,
        volume: 0.08,
      },
      chime: {
        tones: [783.99, 987.77, 1174.66, 1568],
        gap: 0.28,
        repeats: 2,
        duration: 0.7,
        volume: 0.075,
      },
      alarm: {
        tones: [880, 698.46, 880, 698.46],
        gap: 0.22,
        repeats: 4,
        duration: 0.45,
        volume: 0.09,
      },
    };

    const pattern = patterns[preset];
    let cursor = now;

    for (let repeat = 0; repeat < pattern.repeats; repeat += 1) {
      pattern.tones.forEach((tone) => {
        scheduleBellNote(audio, cursor, tone, pattern.duration, pattern.volume);
        cursor += pattern.gap;
      });
      cursor += 0.15;
    }

    const closeDelayMs = Math.max(1500, Math.ceil((cursor - now + 0.3) * 1000));
    window.setTimeout(() => {
      audio.close().catch(() => undefined);
    }, closeDelayMs);

    return true;
  } catch {
    return false;
  }
};

const requestNotificationPermission = async () => {
  if (typeof window === "undefined") return "unsupported" as const;
  if (!("Notification" in window)) return "unsupported" as const;
  if (Notification.permission === "default") {
    try {
      const permission = await Notification.requestPermission();
      return permission;
    } catch {
      return Notification.permission;
    }
  }
  return Notification.permission;
};

const sendBrowserNotification = (title: string, body: string, tag: string) => {
  if (typeof window === "undefined") return;
  if (!("Notification" in window)) return;
  if (Notification.permission !== "granted") return;

  new Notification(title, {
    body,
    tag,
    requireInteraction: true,
  });
};

const vibrateDevice = () => {
  if (typeof navigator === "undefined") return;
  try {
    if ("vibrate" in navigator) {
      navigator.vibrate([300, 150, 300, 150, 650]);
    }
  } catch {
  }
};

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
  const [pendingDueTaskIds, setPendingDueTaskIds] = useState<string[]>([]);
  const [notificationPermission, setNotificationPermission] = useState<
    NotificationPermission | "unsupported"
  >(() => {
    if (typeof window === "undefined") return "unsupported";
    if (!("Notification" in window)) return "unsupported";
    return Notification.permission;
  });
  const tasksRef = useRef<UserTask[]>(tasks);
  const reminderTimeoutRef = useRef<number | null>(null);

  const chooseRingtonePreset = (task: UserTask): RingtonePreset => {
    if (task.category === "outdoor") return "alarm";
    if (task.category === "indoor") return "chime";
    return "bell";
  };

  const enableNotifications = async () => {
    const permission = await requestNotificationPermission();
    setNotificationPermission(permission);
    return permission;
  };

  const testReminder = async (preset: RingtonePreset = "bell") => {
    const permission = await enableNotifications();
    const didPlay = playRingtonePreset(preset);
    vibrateDevice();

    if (permission === "granted") {
      sendBrowserNotification(
        "SkyCoach Reminder Test",
        `Test ${preset} ringtone is active.`,
        "skycoach-reminder-test",
      );
    }

    return {
      didPlay,
      permission,
    };
  };

  const buildRescheduleTarget = (task: UserTask): string => {
    const now = new Date();
    const current = parseScheduledAt(task.scheduledAt) || now;
    const nextDaySameTime = new Date(current.getTime());
    nextDaySameTime.setDate(nextDaySameTime.getDate() + 1);
    nextDaySameTime.setSeconds(0, 0);

    let candidate = nextDaySameTime;
    if (candidate.getTime() <= now.getTime()) {
      candidate = new Date(now.getTime());
      const minutes = candidate.getMinutes();
      const delta = minutes % 30 === 0 ? 30 : 30 - (minutes % 30);
      candidate.setMinutes(minutes + delta, 0, 0);
    }

    return `${formatScheduledDate(candidate)}T${formatScheduledTime(candidate)}:00`;
  };

  const completeDueTask = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
    setPendingDueTaskIds((prev) => prev.filter((id) => id !== taskId));
  };

  const rescheduleDueTask = (taskId: string) => {
    setTasks((prev) =>
      prev.map((task) => {
        if (task.id !== taskId) return task;
        const target = buildRescheduleTarget(task);
        const resolved =
          reserveNextAvailableSlot(prev, target, taskId) || target;
        return {
          ...task,
          completed: false,
          scheduledAt: resolved,
          remindedAt: undefined,
        };
      }),
    );
    setPendingDueTaskIds((prev) => prev.filter((id) => id !== taskId));
  };

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
  }, [tasks]);

  useEffect(() => {
    tasksRef.current = tasks;
  }, [tasks]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const clearReminderTimeout = () => {
      if (reminderTimeoutRef.current !== null) {
        window.clearTimeout(reminderTimeoutRef.current);
        reminderTimeoutRef.current = null;
      }
    };

    const dueTasksAt = (now: number) =>
      tasksRef.current.filter((task) => {
        if (!task.scheduledAt || task.completed || task.remindedAt) {
          return false;
        }

        const dueTime = parseScheduledAt(task.scheduledAt);
        return !!dueTime && dueTime.getTime() <= now;
      });

    const scheduleNextReminderCheck = () => {
      clearReminderTimeout();

      const now = Date.now();
      const nextDueAt = tasksRef.current
        .filter(
          (task) => task.scheduledAt && !task.completed && !task.remindedAt,
        )
        .map((task) => parseScheduledAt(task.scheduledAt))
        .filter((value): value is Date => Boolean(value))
        .map((date) => date.getTime())
        .sort((a, b) => a - b)[0];

      if (!nextDueAt) return;

      const delay = Math.max(0, Math.min(nextDueAt - now, MAX_TIMER_DELAY_MS));
      reminderTimeoutRef.current = window.setTimeout(() => {
        const due = dueTasksAt(Date.now());
        if (due.length) {
          void enableNotifications();

          due.forEach((task) => {
            const when = task.scheduledAt
              ? new Date(task.scheduledAt).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : "now";
            sendBrowserNotification(
              "SkyCoach Reminder",
              `${task.title.trim() || "Scheduled task"} is due at ${when}`,
              `skycoach-task-${task.id}`,
            );
            playRingtonePreset(chooseRingtonePreset(task));
            vibrateDevice();
          });

          const remindedAt = new Date().toISOString();
          const dueIds = new Set(due.map((task) => task.id));
          setTasks((prev) =>
            prev.map((task) =>
              dueIds.has(task.id) ? { ...task, remindedAt } : task,
            ),
          );
          setPendingDueTaskIds((prev) => {
            const merged = new Set(prev);
            dueIds.forEach((id) => merged.add(id));
            return Array.from(merged);
          });
        }

        scheduleNextReminderCheck();
      }, delay + 30);
    };

    void enableNotifications();

    const checkRemindersNow = () => {
      const due = dueTasksAt(Date.now());
      if (!due.length) {
        scheduleNextReminderCheck();
        return;
      }

      void enableNotifications();

      due.forEach((task) => {
        const when = task.scheduledAt
          ? new Date(task.scheduledAt).toLocaleTimeString([], {
              hour: "2-digit",
              minute: "2-digit",
            })
          : "now";
        sendBrowserNotification(
          "SkyCoach Reminder",
          `${task.title.trim() || "Scheduled task"} is due at ${when}`,
          `skycoach-task-${task.id}`,
        );
        playRingtonePreset(chooseRingtonePreset(task));
        vibrateDevice();
      });

      const remindedAt = new Date().toISOString();
      const dueIds = new Set(due.map((task) => task.id));
      setTasks((prev) =>
        prev.map((task) =>
          dueIds.has(task.id) ? { ...task, remindedAt } : task,
        ),
      );
      setPendingDueTaskIds((prev) => {
        const merged = new Set(prev);
        dueIds.forEach((id) => merged.add(id));
        return Array.from(merged);
      });

      scheduleNextReminderCheck();
    };

    checkRemindersNow();
    const intervalId = window.setInterval(checkRemindersNow, SAFETY_POLL_MS);

    const onVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        checkRemindersNow();
      }
    };

    const onWindowFocus = () => {
      checkRemindersNow();
    };

    document.addEventListener("visibilitychange", onVisibilityChange);
    window.addEventListener("focus", onWindowFocus);

    return () => {
      clearReminderTimeout();
      window.clearInterval(intervalId);
      document.removeEventListener("visibilitychange", onVisibilityChange);
      window.removeEventListener("focus", onWindowFocus);
    };
  }, [tasks]);

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

  useEffect(() => {
    const validIds = new Set(
      tasks.filter((task) => !task.completed).map((task) => task.id),
    );
    setPendingDueTaskIds((prev) => prev.filter((id) => validIds.has(id)));
  }, [tasks]);

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
    notificationPermission,
    pendingDueTaskIds,
    enableNotifications,
    testReminder,
    completeDueTask,
    rescheduleDueTask,
    addTask,
    updateTask,
    removeTask,
    clearCompleted,
  };
};

export type TaskStore = ReturnType<typeof useTaskStore>;
