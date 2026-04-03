import { useMemo, useState } from "react";
import type { WeatherData } from "@app-types/api";
import type { TaskCategory, UserTask, WeekForecastDay } from "@app-types/tasks";
import { useGetWeather } from "@hooks/useApi";

interface PlannerPageProps {
  tasks: UserTask[];
  updateTask: (id: string, patch: Partial<UserTask>) => void;
}

const classifyTask = (title: string): TaskCategory => {
  const text = title.toLowerCase();
  const outdoor = [
    "run",
    "jog",
    "walk",
    "soccer",
    "cricket",
    "hike",
    "cycle",
    "wash car",
    "garden",
  ];
  const indoor = [
    "homework",
    "study",
    "read",
    "coding",
    "meeting",
    "movie",
    "clean",
    "cook",
  ];

  if (outdoor.some((word) => text.includes(word))) return "outdoor";
  if (indoor.some((word) => text.includes(word))) return "indoor";
  return "general";
};

const buildWeekForecast = (weather?: WeatherData): WeekForecastDay[] => {
  const baseTemp = weather?.temperature ?? 22;
  const baseWind = weather?.wind_mph ?? 8;
  const conditions = [
    weather?.condition ?? "Clouds",
    "Clear",
    "Clouds",
    "Rain",
    "Clear",
    "Drizzle",
    "Clouds",
  ];

  return Array.from({ length: 7 }, (_, dayOffset) => {
    const date = new Date();
    date.setDate(date.getDate() + dayOffset);
    const condition = conditions[dayOffset % conditions.length];
    return {
      date: date.toISOString().slice(0, 10),
      condition,
      isRaining:
        condition === "Rain" ||
        condition === "Drizzle" ||
        condition === "Thunderstorm",
      temperature:
        Math.round((baseTemp + Math.sin(dayOffset * 0.9) * 4) * 10) / 10,
      windMph: Math.round((baseWind + Math.cos(dayOffset * 0.7) * 3) * 10) / 10,
    };
  });
};

const scoreTaskForDay = (
  category: TaskCategory,
  day: WeekForecastDay,
): { score: number; reason: string } => {
  if (category === "outdoor") {
    if (day.isRaining)
      return { score: 20, reason: "Rain risk - keep indoor backup" };
    if (day.windMph > 15) return { score: 45, reason: "Windy conditions" };
    if (day.temperature < 8 || day.temperature > 32)
      return { score: 55, reason: "Temperature not ideal" };
    return { score: 90, reason: "Strong outdoor weather" };
  }

  if (category === "indoor") {
    if (day.isRaining)
      return { score: 88, reason: "Rainy day suits indoor tasks" };
    return { score: 72, reason: "Indoor task flexible" };
  }

  return {
    score: day.isRaining ? 65 : 80,
    reason: "General task with moderate flexibility",
  };
};

export default function PlannerPage({ tasks, updateTask }: PlannerPageProps) {
  const [city, setCity] = useState("New York");
  const requestedCity = city.trim();
  const { data: weather, isFetching } = useGetWeather(requestedCity);
  const forecast = useMemo(() => buildWeekForecast(weather), [weather]);

  const sequenced = useMemo(() => {
    const candidates = tasks.filter((task) => !task.completed);

    return candidates
      .map((task) => {
        const category = classifyTask(task.title);
        const ranked = forecast
          .map((day) => ({ day, ...scoreTaskForDay(category, day) }))
          .sort((a, b) => b.score - a.score);

        const best = ranked[0];
        return {
          taskId: task.id,
          title: task.title,
          category,
          recommendedDate: best.day.date,
          confidence: best.score,
          reason: best.reason,
        };
      })
      .sort((a, b) => b.confidence - a.confidence);
  }, [tasks, forecast]);

  const applyRecommendations = () => {
    sequenced.forEach((item, index) => {
      const hour = 9 + (index % 9);
      const slot = `${item.recommendedDate}T${String(hour).padStart(2, "0")}:00:00`;
      updateTask(item.taskId, { scheduledAt: slot });
    });
  };

  return (
    <div className="space-y-6">
      <section className="card space-y-3">
        <h2 className="text-xl font-bold">Weather-Task Sequencer (7 Days)</h2>
        <p className="text-sm text-slate-400">
          This model maps your pending tasks against a predictable 1-week
          weather outlook and suggests the best sequence.
        </p>
        <p className="text-xs text-cyan-300">
          Recommendations are currently based on:{" "}
          {weather?.city || requestedCity || "New York"}
          {isFetching ? " (updating...)" : ""}
        </p>
        <div className="max-w-sm">
          <label
            htmlFor="forecast-city"
            className="block text-xs text-slate-400 mb-1">
            Forecast City
          </label>
          <input
            id="forecast-city"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            aria-label="Forecast city"
            title="Forecast city"
            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg"
          />
        </div>
      </section>

      <section className="card">
        <h3 className="text-lg font-semibold mb-3">Upcoming Week Forecast</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-2">
          {forecast.map((day) => (
            <div
              key={day.date}
              className="p-2 rounded-lg bg-slate-800/60 border border-slate-700 text-xs">
              <p className="text-slate-300">
                {new Date(day.date).toLocaleDateString(undefined, {
                  weekday: "short",
                })}
              </p>
              <p className="text-slate-500">{day.date}</p>
              <p className="mt-1">{day.condition}</p>
              <p>{day.temperature.toFixed(1)}°C</p>
              <p>{day.windMph.toFixed(1)} mph</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">Recommended Task Sequence</h3>
          <button
            type="button"
            onClick={applyRecommendations}
            disabled={sequenced.length === 0}
            className="px-3 py-2 text-xs rounded-lg bg-cyan-500/20 border border-cyan-400 text-cyan-200 disabled:opacity-50 disabled:cursor-not-allowed">
            Apply to Todo/Timetable
          </button>
        </div>
        {sequenced.length === 0 ? (
          <p className="text-slate-400">
            No pending tasks found. Add tasks in Todo List.
          </p>
        ) : (
          sequenced.map((item, index) => (
            <div
              key={item.taskId}
              className="p-3 bg-slate-800/50 border border-slate-700 rounded-lg">
              <p className="text-sm text-slate-400">#{index + 1}</p>
              <p className="font-medium">{item.title}</p>
              <p className="text-xs text-slate-400 mt-1">
                Category: {item.category}
              </p>
              <p className="text-sm text-cyan-300 mt-1">
                Best day: {item.recommendedDate}
              </p>
              <p className="text-xs text-slate-400">
                Confidence: {item.confidence}% • {item.reason}
              </p>
            </div>
          ))
        )}
      </section>
    </div>
  );
}
