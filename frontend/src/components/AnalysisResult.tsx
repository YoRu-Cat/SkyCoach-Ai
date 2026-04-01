import React from "react";
import type { AnalysisResponse } from "@types/api";
import TaskCard from "./TaskCard";
import WeatherCard from "./WeatherCard";
import ScoreCard from "./ScoreCard";
import AlternativesCard from "./AlternativesCard";

interface AnalysisResultProps {
  data: AnalysisResponse;
}

export default function AnalysisResult({ data }: AnalysisResultProps) {
  return (
    <div className="space-y-6 animate-fade-in">
      {/* Task Analysis */}
      <TaskCard task={data.task} />

      {/* Weather Information */}
      <WeatherCard weather={data.weather} />

      {/* Core Score */}
      <ScoreCard score={data.score_result} />

      {/* Alternatives */}
      {data.alternatives && data.alternatives.length > 0 && (
        <AlternativesCard
          alternatives={data.alternatives}
          classification={data.task.classification}
        />
      )}
    </div>
  );
}
