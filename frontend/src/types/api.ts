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
  bonuses: Array<[string, number, string]>;
  penalties: Array<[string, number, string]>;
  recommendation: string;
}

export interface AnalysisResponse {
  task: TaskAnalysis;
  weather: WeatherData;
  score_result: SkyScoreResult;
  alternatives: string[];
}
