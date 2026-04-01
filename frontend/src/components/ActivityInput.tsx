import React, { useState } from "react";

interface ActivityInputProps {
  onAnalyze: (activity: string, city: string) => void;
  isLoading: boolean;
}

export default function ActivityInput({
  onAnalyze,
  isLoading,
}: ActivityInputProps) {
  const [activity, setActivity] = useState("");
  const [city, setCity] = useState("New York");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activity.trim()) {
      onAnalyze(activity.trim(), city.trim());
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="card space-y-6 sticky top-8">
        <div>
          <h2 className="text-xl font-bold mb-4 text-slate-100">
            What's your plan?
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
            Describe the activity you're planning, even if it's incomplete
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Location
          </label>
          <input
            type="text"
            value={city}
            onChange={(e) => setCity(e.target.value)}
            placeholder="Enter city name..."
            className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500 focus:ring-opacity-20"
            disabled={isLoading}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading || !activity.trim()}
          className="w-full btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed">
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
