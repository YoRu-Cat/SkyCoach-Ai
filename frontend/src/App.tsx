import { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import {
  API_BASE_URL,
  healthCheckWithRetry,
  onApiError,
} from "@services/api";
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

type ApiState = "checking" | "online" | "offline";

function App() {
  const [themeMode] = useState<ThemeMode>(() => loadTheme());
  const [apiState, setApiState] = useState<ApiState>("checking");
  const [isOnline, setIsOnline] = useState<boolean>(
    typeof navigator !== "undefined" ? navigator.onLine : true,
  );
  const [bannerDismissed, setBannerDismissed] = useState(false);
  const [errorToast, setErrorToast] = useState<string | null>(null);

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", themeMode);
  }, [themeMode]);

  useEffect(() => {
    const updateOnline = () => setIsOnline(navigator.onLine);
    window.addEventListener("online", updateOnline);
    window.addEventListener("offline", updateOnline);
    return () => {
      window.removeEventListener("online", updateOnline);
      window.removeEventListener("offline", updateOnline);
    };
  }, []);

  // Background health probe. UI renders immediately; result only drives
  // the offline banner.
  useEffect(() => {
    let cancelled = false;
    const run = async () => {
      const ok = await healthCheckWithRetry();
      if (!cancelled) setApiState(ok ? "online" : "offline");
    };
    run();
    const interval = window.setInterval(() => {
      if (apiState === "offline") {
        void run();
      }
    }, 60_000);
    return () => {
      cancelled = true;
      window.clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Toast plumbing for API errors.
  useEffect(() => {
    const unsubscribe = onApiError(({ status, message }) => {
      if (status === 429) {
        setErrorToast("Too many requests - please slow down.");
      } else if (status && status >= 500) {
        setErrorToast("Backend error - retrying may help.");
      } else if (status === null) {
        setErrorToast("Network unreachable - check your connection.");
      } else {
        setErrorToast(message.slice(0, 140));
      }
      window.setTimeout(() => setErrorToast(null), 5000);
    });
    return () => {
      unsubscribe();
    };
  }, []);

  const showBanner =
    !bannerDismissed && (apiState === "offline" || !isOnline);

  return (
    <QueryClientProvider client={queryClient}>
      {showBanner ? (
        <div
          role="status"
          className="fixed top-0 inset-x-0 z-50 px-4 py-2 text-sm flex items-center justify-center gap-3 bg-amber-500/95 text-amber-950 shadow-lg">
          <span>
            {!isOnline
              ? "You appear to be offline."
              : `Backend at ${API_BASE_URL || "/api"} is currently unreachable. The service may need a moment to start up; retrying every minute.`}
          </span>
          <button
            type="button"
            onClick={() => setBannerDismissed(true)}
            className="px-2 py-0.5 rounded bg-amber-900/20 hover:bg-amber-900/40">
            Dismiss
          </button>
        </div>
      ) : null}
      {errorToast ? (
        <div
          role="alert"
          className="fixed bottom-4 right-4 z-50 max-w-sm px-4 py-3 rounded-lg bg-red-600/95 text-white shadow-xl">
          {errorToast}
        </div>
      ) : null}
      <AppShell />
    </QueryClientProvider>
  );
}

export default App;
