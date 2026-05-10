import axios from "axios";
import type {
  TaskAnalysis,
  WeatherData,
  AnalysisResponse,
  ChatMessage,
  ChatDraft,
  ChatTaskContext,
  ChatAssistantResponse,
  BackendCliResponse,
} from "@app-types/api";

export interface AnalysisParams {
  activityText: string;
  city: string;
  latitude?: number;
  longitude?: number;
}

// Backend base URL resolution:
//   1. An explicit VITE_API_URL from .env.production or the hosting UI.
//   2. An empty string in any production build, so the SPA uses relative
//      '/api' URLs and the hosting platform's proxy handles the redirect.
//   3. A localhost fallback for `npm run dev`.
const explicitApiUrl =
  (import.meta.env.VITE_API_URL ?? "").toString().trim();

export const API_BASE_URL = explicitApiUrl
  ? explicitApiUrl.replace(/\/$/, "")
  : import.meta.env.PROD
    ? ""
    : "http://127.0.0.1:8012";

const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api`,
  headers: {
    "Content-Type": "application/json",
  },
  // Generous timeout so a backend that takes a moment to wake up after
  // idle still resolves successfully.
  timeout: 25000,
});

// Pub/sub for API-level errors. UI surfaces (toasts, banners) subscribe
// here so they can react to network or server failures without each
// individual call site having to handle them.
type ApiErrorListener = (info: {
  status: number | null;
  message: string;
  url: string;
}) => void;
const apiErrorListeners = new Set<ApiErrorListener>();
export const onApiError = (listener: ApiErrorListener) => {
  apiErrorListeners.add(listener);
  return () => apiErrorListeners.delete(listener);
};

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status ?? null;
    const url = error?.config?.url ?? "";
    const message =
      error?.response?.data?.detail ||
      error?.message ||
      "Request failed";
    apiErrorListeners.forEach((listener) =>
      listener({ status, message, url }),
    );
    return Promise.reject(error);
  },
);

const useDemoWeather = import.meta.env.VITE_USE_DEMO_WEATHER === "true";
const openAIModel = import.meta.env.VITE_OPENAI_MODEL || "gpt-4o-mini";

export const analyzeTask = async (text: string): Promise<TaskAnalysis> => {
  const response = await apiClient.post("/analyze-task", {
    text,
    use_openai: false,
    openai_api_key: null,
    openai_model: null,
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
    const response = await apiClient.get("/health", { timeout: 6000 });
    return response.data?.status === "healthy";
  } catch {
    return false;
  }
};

/**
 * Non-blocking health probe with retry. Tolerates the short delay that
 * a backend may need to wake up after a period of inactivity.
 */
export const healthCheckWithRetry = async (
  attempts: number = 4,
  delayMs: number = 4000,
): Promise<boolean> => {
  for (let i = 0; i < attempts; i++) {
    if (await healthCheck()) return true;
    if (i < attempts - 1) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  return false;
};

export const chatAssistant = async (
  messages: ChatMessage[],
  draft: ChatDraft,
  taskContext: ChatTaskContext[],
): Promise<ChatAssistantResponse> => {
  const response = await apiClient.post("/chat-assistant", {
    messages,
    draft,
    task_context: taskContext,
    today_iso: new Date().toISOString().slice(0, 10),
    use_openai: true,
    openai_api_key: null,
    openai_model: openAIModel,
  });
  return response.data;
};

export const runBackendCliCommand = async (
  command: string,
): Promise<BackendCliResponse> => {
  const response = await apiClient.post("/backend-cli", {
    command,
  });
  return response.data;
};
