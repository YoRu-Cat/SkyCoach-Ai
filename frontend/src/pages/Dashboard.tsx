import { useEffect, useRef, useState } from "react";
import { gsap } from "gsap";
import { useFullAnalysis } from "@hooks/useApi";
import ActivityInput from "@components/ActivityInput";
import AnalysisResult from "@components/AnalysisResult";
import Header from "@components/Header";
import WeatherBackground from "@components/WeatherBackground";
import { usePreferredCity } from "@hooks/usePreferredCity";
import type { AnalysisResponse } from "@app-types/api";

interface AnalyzeInput {
  activity: string;
  city: string;
  latitude?: number;
  longitude?: number;
}

interface DashboardProps {
  embedded?: boolean;
}

export default function Dashboard({ embedded = false }: DashboardProps) {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const { mutate: runAnalysis, isLoading } = useFullAnalysis();
  const { setCity } = usePreferredCity();
  const layoutRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!layoutRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".input-panel",
        { opacity: 0, x: -24 },
        { opacity: 1, x: 0, duration: 0.7, ease: "power2.out" },
      );
      gsap.fromTo(
        ".result-shell",
        { opacity: 0, x: 24 },
        { opacity: 1, x: 0, duration: 0.7, ease: "power2.out", delay: 0.1 },
      );
    }, layoutRef);

    return () => ctx.revert();
  }, []);

  const handleAnalyze = ({
    activity,
    city,
    latitude,
    longitude,
  }: AnalyzeInput) => {
    runAnalysis(
      {
        activityText: activity,
        city,
        latitude,
        longitude,
      },
      {
        onSuccess: (data) => {
          setAnalysis(data);
          if (data.weather?.city) {
            setCity(data.weather.city);
          }
        },
        onError: (error) => {
          console.error("Analysis failed:", error);
        },
      },
    );
  };

  const handleUseSuggestion = (value: string) => {
    const city = analysis?.weather.city || "New York";
    runAnalysis(
      {
        activityText: value,
        city,
      },
      {
        onSuccess: (data) => {
          setAnalysis(data);
          if (data.weather?.city) {
            setCity(data.weather.city);
          }
        },
        onError: (error) => {
          console.error("Suggestion re-analysis failed:", error);
        },
      },
    );
  };

  return (
    <div className={embedded ? "pb-4" : "min-h-screen pb-12"}>
      <WeatherBackground weather={analysis?.weather} />
      {!embedded ? <Header /> : null}

      <div
        ref={layoutRef}
        className={
          embedded
            ? "max-w-6xl mx-auto px-2 sm:px-3 lg:px-4 py-4"
            : "max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8"
        }>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-1 input-panel">
            <ActivityInput onAnalyze={handleAnalyze} isLoading={isLoading} />
          </div>

          <div className="lg:col-span-2 result-shell">
            {isLoading ? (
              <div className="card flex items-center justify-center h-96 animated-card-border">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-500 mx-auto mb-4"></div>
                  <p className="text-slate-300">Analyzing your activity...</p>
                </div>
              </div>
            ) : analysis ? (
              <AnalysisResult
                data={analysis}
                onUseSuggestion={handleUseSuggestion}
              />
            ) : (
              <div className="card text-center py-12 text-slate-300 animated-card-border floating-panel">
                <p>Enter an activity and location to get started</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
