import axios from "axios";
import type { TaskAnalysis, WeatherData, AnalysisResponse } from "@app-types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

export const analyzeTask = async (text: string): Promise<TaskAnalysis> => {
  const response = await apiClient.post("/analyze-task", {
    text,
    use_openai: false,
    openai_api_key: null,
  });
  return response.data;
};

export const getWeather = async (city: string): Promise<WeatherData> => {
  const response = await apiClient.post("/weather", {
    city,
    use_demo: true,
    api_key: null,
  });
  return response.data;
};

export const fullAnalysis = async (
  activityText: string,
  city: string,
): Promise<AnalysisResponse> => {
  const response = await apiClient.post("/analyze", {
    activity_text: activityText,
    city,
    use_openai: false,
    weather_api_key: null,
    openai_api_key: null,
    use_demo_weather: true,
  });
  return response.data;
};

export const getAlternatives = async (
  classification: string,
): Promise<string[]> => {
  const response = await apiClient.get("/alternatives", {
    params: {
      classification,
      weather_city: "New York",
      use_demo: true,
    },
  });
  return response.data.suggestions;
};

export const healthCheck = async (): Promise<boolean> => {
  try {
    const response = await apiClient.get("/health");
    return response.data.status === "healthy";
  } catch {
    return false;
  }
};
