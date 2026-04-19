import { useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { API_BASE_URL, healthCheck } from "@services/api";
import AppShell from "@components/AppShell";
import "@styles/globals.css";

type ThemeMode = "dark" | "light";
const THEME_STORAGE_KEY = "skycoach_theme_v1";

const loadTheme = (): ThemeMode => {
  if (typeof window === "undefined") return "dark";
  const value = window.localStorage.getItem(THEME_STORAGE_KEY);
  return value === "light" ? "light" : "dark";
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  const [isHealthy, setIsHealthy] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [themeMode] = useState<ThemeMode>(() => loadTheme());

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", themeMode);
  }, [themeMode]);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const healthy = await healthCheck();
        setIsHealthy(healthy);
      } catch (error) {
        console.error("API health check failed:", error);
        setIsHealthy(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkApi();
  }, []);

  if (isLoading) {
    return (
      <div
        className={`min-h-screen flex items-center justify-center ${
          themeMode === "light"
            ? "theme-light bg-[#f6f2fc] text-[#210f3c]"
            : "theme-dark bg-gradient-to-br from-dark_amethyst-500 via-midnight_violet-500 to-midnight_violet-300 text-alabaster_grey-900"
        }`}>
        <div className="card text-center">
          <div
            className={`animate-spin rounded-full h-12 w-12 border-b-2 mx-auto mb-4 ${
              themeMode === "light" ? "border-[#7c45b8]" : "border-[#bb4dfb]"
            }`}
          />
          <p
            className={
              themeMode === "light" ? "text-[#311a53]" : "text-slate-300"
            }>
            Initializing SkyCoach...
          </p>
        </div>
      </div>
    );
  }

  if (!isHealthy) {
    return (
      <div
        className={`min-h-screen flex items-center justify-center px-4 ${
          themeMode === "light"
            ? "theme-light bg-[#f6f2fc] text-[#210f3c]"
            : "theme-dark bg-gradient-to-br from-dark_amethyst-500 via-midnight_violet-500 to-midnight_violet-300 text-alabaster_grey-900"
        }`}>
        <div
          className={`card max-w-md w-full border ${
            themeMode === "light"
              ? "border-[#b596e5]/55"
              : "border-[#5f2e86]/45"
          }`}>
          <h1
            className={`text-2xl font-bold mb-4 ${
              themeMode === "light" ? "text-[#5f2a8c]" : "text-red-300"
            }`}>
            Connection Error
          </h1>
          <p
            className={`mb-4 ${
              themeMode === "light" ? "text-[#311a53]" : "text-slate-300"
            }`}>
            Could not connect to the SkyCoach API backend.
          </p>
          <p
            className={`text-sm ${
              themeMode === "light" ? "text-[#4a2a76]" : "text-slate-400"
            }`}>
            Make sure the backend server is running on{" "}
            <code
              className={`px-2 py-1 rounded ${
                themeMode === "light"
                  ? "bg-[#e7dcf8] text-[#3c1f67]"
                  : "bg-slate-800 text-slate-200"
              }`}>
              {API_BASE_URL}
            </code>
          </p>
          <button
            onClick={() => window.location.reload()}
            className="btn btn-primary mt-6 w-full">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <AppShell />
    </QueryClientProvider>
  );
}

export default App;
