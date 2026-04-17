import type { UserTask } from "@app-types/tasks";

const SLOT_STEP_MINUTES = 30;
const LOOKAHEAD_DAYS = 30;

const pad = (value: number) => String(value).padStart(2, "0");

const formatLocalDateTime = (date: Date): string => {
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  const hours = pad(date.getHours());
  const minutes = pad(date.getMinutes());
  return `${year}-${month}-${day}T${hours}:${minutes}:00`;
};

export const buildLocalScheduledAt = (date: string, time: string): string =>
  `${date}T${time}:00`;

export const parseScheduledAt = (scheduledAt?: string | null): Date | null => {
  if (!scheduledAt) return null;
  const parsed = new Date(scheduledAt);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

export const formatScheduledDate = (date: Date): string =>
  `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;

export const formatScheduledTime = (date: Date): string =>
  `${pad(date.getHours())}:${pad(date.getMinutes())}`;

const sameMinute = (left: Date, right: Date): boolean =>
  left.getFullYear() === right.getFullYear() &&
  left.getMonth() === right.getMonth() &&
  left.getDate() === right.getDate() &&
  left.getHours() === right.getHours() &&
  left.getMinutes() === right.getMinutes();

const isSlotOccupied = (
  tasks: UserTask[],
  candidate: Date,
  excludeTaskId?: string,
): boolean =>
  tasks.some((task) => {
    if (excludeTaskId && task.id === excludeTaskId) return false;
    const scheduled = parseScheduledAt(task.scheduledAt);
    return scheduled ? sameMinute(scheduled, candidate) : false;
  });

export const reserveNextAvailableSlot = (
  tasks: UserTask[],
  targetScheduledAt?: string | null,
  excludeTaskId?: string,
): string | undefined => {
  const target = parseScheduledAt(targetScheduledAt);
  if (!target) return undefined;

  const candidate = new Date(target.getTime());
  const limit = new Date(target.getTime());
  limit.setDate(limit.getDate() + LOOKAHEAD_DAYS);

  while (candidate <= limit) {
    if (!isSlotOccupied(tasks, candidate, excludeTaskId)) {
      return formatLocalDateTime(candidate);
    }

    candidate.setMinutes(candidate.getMinutes() + SLOT_STEP_MINUTES);
  }

  return formatLocalDateTime(target);
};
