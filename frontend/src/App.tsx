import { useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "react-query";
import { healthCheck } from "@services/api";
import Dashboard from "@pages/Dashboard";
import "@styles/globals.css";

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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center">
        <div className="card text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
          <p className="text-slate-300">Initializing SkyCoach...</p>
        </div>
      </div>
    );
  }

  if (!isHealthy) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 flex items-center justify-center px-4">
        <div className="card max-w-md">
          <h1 className="text-2xl font-bold text-red-400 mb-4">
            Connection Error
          </h1>
          <p className="text-slate-300 mb-4">
            Could not connect to the SkyCoach API backend.
          </p>
          <p className="text-slate-400 text-sm">
            Make sure the backend server is running on{" "}
            <code className="bg-slate-800 px-2 py-1 rounded">
              http://localhost:8000
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
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Dashboard />
      </div>
    </QueryClientProvider>
  );
}

export default App;
