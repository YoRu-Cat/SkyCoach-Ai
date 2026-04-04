export interface UserTask {
  id: string;
  title: string;
  notes?: string;
  createdAt: string;
  completed: boolean;
  scheduledAt?: string;
}

export type TaskCategory = "indoor" | "outdoor";

export interface WeekForecastDay {
  date: string;
  condition: string;
  isRaining: boolean;
  temperature: number;
  windMph: number;
}

export interface SequencedTask {
  taskId: string;
  title: string;
  category: TaskCategory;
  recommendedDate: string;
  confidence: number;
  reason: string;
}
