export interface TaskAnalysis {
  original_text: string;
  cleaned_text: string;
  activity: string;
  classification: "Indoor" | "Outdoor";
  confidence: number;
  reasoning: string;
  needs_clarification: boolean;
  issue?: string;
  suggested_activity?: string;
  suggested_classification?: string;
  suggestion_confidence: number;
}

export interface WeatherData {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  temperature: number;
  feels_like: number;
  humidity: number;
  rain_1h: number;
  is_raining: boolean;
  wind_speed: number;
  wind_mph: number;
  condition: string;
  description: string;
  icon_code: string;
  units: string;
  temp_unit: string;
}

export interface SkyScoreResult {
  score: number;
  classification: "Indoor" | "Outdoor";
  weather_factors: string[];
  bonuses: FactorDetail[];
  penalties: FactorDetail[];
  recommendation: string;
}

export interface FactorDetail {
  name: string;
  value: number;
  description: string;
}

export interface AnalysisResponse {
  task: TaskAnalysis;
  weather: WeatherData;
  score_result: SkyScoreResult;
  alternatives: Array<[string, string]>;
}

export type ChatRole = "user" | "assistant" | "system";

export interface ChatMessage {
  role: ChatRole;
  content: string;
}

export interface ChatDraft {
  task_title?: string | null;
  date?: string | null;
  time?: string | null;
  notes?: string | null;
}

export type ChatNavigateTo =
  | "dashboard"
  | "todo"
  | "timetable"
  | "planner"
  | "chat";

export interface ChatAssistantResponse {
  assistant_message: string;
  draft: ChatDraft;
  missing_fields: Array<"task_title" | "date" | "time">;
  requires_confirmation: boolean;
  create_task: boolean;
  navigate_to: ChatNavigateTo;
  reset_draft: boolean;
}
