import { useEffect, useState } from "react";
import { usePreferredCity } from "@hooks/usePreferredCity";

interface LocationCoords {
  latitude: number;
  longitude: number;
}

interface AnalyzeInput {
  activity: string;
  city: string;
  latitude?: number;
  longitude?: number;
}

interface ActivityInputProps {
  onAnalyze: (input: AnalyzeInput) => void;
  isLoading: boolean;
}

export default function ActivityInput({
  onAnalyze,
  isLoading,
}: ActivityInputProps) {
  const [activity, setActivity] = useState("");
  const { city, setCity, defaultCity, location, setLocation, clearLocation } =
    usePreferredCity();
  const [locationMode, setLocationMode] = useState<"auto" | "manual">(
    location.mode,
  );
  const [coords, setCoords] = useState<LocationCoords | null>(
    location.latitude !== undefined && location.longitude !== undefined
      ? { latitude: location.latitude, longitude: location.longitude }
      : null,
  );
  const [locationStatus, setLocationStatus] = useState(
    "Detecting your location...",
  );
  const quickActivities = [
    "playing soccer",
    "washing car",
    "running in park",
    "doing homework",
    "jogging",
    "cycling",
  ];

  const detectLocation = () => {
    if (!("geolocation" in navigator)) {
      setLocationStatus(
        "Geolocation is not supported by this browser. Switch to manual location.",
      );
      return;
    }

    setLocationStatus("Detecting your location...");

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const nextCoords = {
          latitude: Number(position.coords.latitude.toFixed(6)),
          longitude: Number(position.coords.longitude.toFixed(6)),
        };
        setCoords(nextCoords);
        setLocation({
          latitude: nextCoords.latitude,
          longitude: nextCoords.longitude,
          mode: "auto",
        });
        setLocationStatus(
          `Using precise location (${nextCoords.latitude.toFixed(3)}, ${nextCoords.longitude.toFixed(3)})`,
        );
      },
      () => {
        setCoords(null);
        setLocation({
          latitude: undefined,
          longitude: undefined,
          mode: "auto",
        });
        setLocationStatus(
          "Location permission denied or unavailable. Switch to manual location.",
        );
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000,
      },
    );
  };

  useEffect(() => {
    if (locationMode === "auto") {
      detectLocation();
    }
  }, [locationMode]);

  useEffect(() => {
    setLocation({ mode: locationMode });
  }, [locationMode, setLocation]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activity.trim()) {
      if (locationMode === "auto" && coords) {
        onAnalyze({
          activity: activity.trim(),
          city: city.trim() || defaultCity,
          latitude: coords.latitude,
          longitude: coords.longitude,
        });
        return;
      }

      onAnalyze({
        activity: activity.trim(),
        city: city.trim() || defaultCity,
      });
    }
  };

  const handleClearSavedLocation = () => {
    clearLocation();
    setCoords(null);
    setLocationMode("auto");
    setLocation({
      city: defaultCity,
      latitude: undefined,
      longitude: undefined,
      mode: "auto",
    });
    setLocationStatus("Saved location cleared. Detecting your location...");
    detectLocation();
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="card space-y-6 sticky top-8 animated-card-border floating-panel">
        <div>
          <h2 className="text-xl font-bold mb-4 text-slate-100">
            What&apos;s your plan?
          </h2>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Activity Description
          </label>
          <textarea
            value={activity}
            onChange={(e) => setActivity(e.target.value)}
            placeholder="e.g., playing soccer, doing homework, washing car..."
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500 focus:ring-opacity-20 resize-none"
            rows={4}
            disabled={isLoading}
          />
          <p className="mt-2 text-xs text-slate-400">
            Describe the activity you&apos;re planning, even if it&apos;s
            incomplete
          </p>
          <div className="flex flex-wrap gap-2 mt-3">
            {quickActivities.map((item) => (
              <button
                key={item}
                type="button"
                disabled={isLoading}
                onClick={() => setActivity(item)}
                className="px-2.5 py-1 text-xs rounded-full bg-slate-800 border border-slate-700 text-slate-300 hover:border-cyan-500/60 hover:text-cyan-300 transition-all hover:-translate-y-0.5">
                {item}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Location
          </label>

          <div className="grid grid-cols-2 gap-2 mb-3">
            <button
              type="button"
              disabled={isLoading}
              onClick={() => setLocationMode("auto")}
              className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                locationMode === "auto"
                  ? "bg-cyan-500/20 border-cyan-400 text-cyan-200"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:border-cyan-500/60"
              }`}>
              Auto (GPS)
            </button>
            <button
              type="button"
              disabled={isLoading}
              onClick={() => setLocationMode("manual")}
              className={`px-3 py-2 text-sm rounded-lg border transition-colors ${
                locationMode === "manual"
                  ? "bg-cyan-500/20 border-cyan-400 text-cyan-200"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:border-cyan-500/60"
              }`}>
              Manual (City)
            </button>
          </div>

          {locationMode === "auto" ? (
            <div className="space-y-2">
              <div className="px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 text-sm">
                {locationStatus}
              </div>
              <button
                type="button"
                disabled={isLoading}
                onClick={detectLocation}
                className="w-full px-3 py-2 text-xs rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:border-cyan-500/60 hover:text-cyan-300 transition-colors">
                Retry Location Detection
              </button>
            </div>
          ) : (
            <input
              type="text"
              value={city}
              onChange={(e) => {
                const nextCity = e.target.value;
                setCity(nextCity);
                setLocation({
                  city: nextCity,
                  mode: "manual",
                  latitude: undefined,
                  longitude: undefined,
                });
              }}
              placeholder="Enter city name..."
              className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500 focus:ring-opacity-20"
              disabled={isLoading}
            />
          )}

          <button
            type="button"
            disabled={isLoading}
            onClick={handleClearSavedLocation}
            className="mt-3 w-full px-3 py-2 text-xs rounded-lg bg-slate-900 border border-slate-700 text-slate-300 hover:border-rose-500/60 hover:text-rose-300 transition-colors">
            Clear Saved Location
          </button>
        </div>

        <button
          type="submit"
          disabled={isLoading || !activity.trim()}
          className="w-full btn btn-primary btn-shimmer disabled:opacity-50 disabled:cursor-not-allowed">
          {isLoading ? "Analyzing..." : "Analyze Activity"}
        </button>

        <div className="pt-4 border-t border-slate-700">
          <p className="text-xs text-slate-500 text-center">
            Powered by SkyCoach AI • Auto-corrections enabled
          </p>
        </div>
      </div>
    </form>
  );
}
