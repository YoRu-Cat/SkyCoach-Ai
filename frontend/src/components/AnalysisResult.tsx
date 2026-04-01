import { useEffect, useRef } from "react";
import { gsap } from "gsap";
import type { AnalysisResponse } from "@app-types/api";
import TaskCard from "./TaskCard";
import WeatherCard from "./WeatherCard";
import ScoreCard from "./ScoreCard";
import AlternativesCard from "./AlternativesCard";

interface AnalysisResultProps {
  data: AnalysisResponse;
  onUseSuggestion?: (value: string) => void;
}

export default function AnalysisResult({
  data,
  onUseSuggestion,
}: AnalysisResultProps) {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const ctx = gsap.context(() => {
      gsap.fromTo(
        ".analysis-panel",
        { opacity: 0, y: 24 },
        {
          opacity: 1,
          y: 0,
          duration: 0.55,
          ease: "power2.out",
          stagger: 0.1,
        },
      );
    }, containerRef);

    return () => ctx.revert();
  }, [data]);

  return (
    <div ref={containerRef} className="space-y-6">
      {/* Task Analysis */}
      <div className="analysis-panel">
        <TaskCard task={data.task} onUseSuggestion={onUseSuggestion} />
      </div>

      {/* Weather Information */}
      <div className="analysis-panel">
        <WeatherCard weather={data.weather} />
      </div>

      {/* Core Score */}
      <div className="analysis-panel">
        <ScoreCard score={data.score_result} />
      </div>

      {/* Alternatives */}
      {data.alternatives && data.alternatives.length > 0 && (
        <div className="analysis-panel">
          <AlternativesCard
            alternatives={data.alternatives}
            classification={data.task.classification}
          />
        </div>
      )}
    </div>
  );
}
