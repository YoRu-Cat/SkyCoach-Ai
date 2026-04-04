import axios from "axios";
import type {
  TaskAnalysis,
  WeatherData,
  AnalysisResponse,
  ChatMessage,
  ChatDraft,
  ChatAssistantResponse,
} from "@app-types/api";

export interface AnalysisParams {
  activityText: string;
  city: string;
  latitude?: number;
  longitude?: number;
}

const isNetlifyRuntime =
  typeof window !== "undefined" &&
  window.location.hostname.endsWith("netlify.app");

export const API_BASE_URL = isNetlifyRuntime
  ? ""
  : import.meta.env.VITE_API_URL ||
    (import.meta.env.PROD
      ? "https://skycoach-ai.onrender.com"
      : "http://localhost:8000");

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
});

const useDemoWeather = import.meta.env.VITE_USE_DEMO_WEATHER === "true";
const openAIModel = import.meta.env.VITE_OPENAI_MODEL || "gpt-4o-mini";

export const analyzeTask = async (
  text: string,
  useOpenAI = false,
  model = openAIModel,
): Promise<TaskAnalysis> => {
  const response = await apiClient.post("/analyze-task", {
    text,
    use_openai: useOpenAI,
    openai_api_key: null,
    openai_model: model,
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
  params: AnalysisParams,
): Promise<AnalysisResponse> => {
  const { activityText, city, latitude, longitude } = params;

  const response = await apiClient.post("/analyze", {
    activity_text: activityText,
    city,
    latitude,
    longitude,
    use_openai: false,
    weather_api_key: null,
    openai_api_key: null,
    openai_model: openAIModel,
    use_demo_weather: useDemoWeather,
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

export const chatAssistant = async (
  messages: ChatMessage[],
  draft: ChatDraft,
): Promise<ChatAssistantResponse> => {
  const response = await apiClient.post("/chat-assistant", {
    messages,
    draft,
    today_iso: new Date().toISOString().slice(0, 10),
    use_openai: true,
    openai_api_key: null,
    openai_model: openAIModel,
  });
  return response.data;
};
