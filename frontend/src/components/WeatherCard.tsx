import React from "react";
import type { WeatherData } from "@types/api";

interface WeatherCardProps {
  weather: WeatherData;
}

const getWeatherEmoji = (condition: string): string => {
  const emoji: Record<string, string> = {
    Clear: "☀️",
    Clouds: "☁️",
    Rain: "🌧️",
    Drizzle: "🌦️",
    Thunderstorm: "⛈️",
    Snow: "❄️",
    Mist: "🌫️",
    Fog: "🌫️",
  };
  return emoji[condition] || "🌤️";
};

export default function WeatherCard({ weather }: WeatherCardProps) {
  return (
    <div className="card glow-cyan">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-100">
          {getWeatherEmoji(weather.condition)} Weather
        </h3>
        <p className="text-sm text-slate-400">
          {weather.city}, {weather.country}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">
            Temperature
          </p>
          <p className="text-2xl font-bold text-cyan-400 mt-2">
            {weather.temperature.toFixed(1)}
            {weather.temp_unit}
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Feels like {weather.feels_like.toFixed(1)}
            {weather.temp_unit}
          </p>
        </div>

        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">
            Condition
          </p>
          <p className="text-lg font-semibold text-slate-200 mt-2 capitalize">
            {weather.description}
          </p>
        </div>

        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">
            Humidity
          </p>
          <p className="text-2xl font-bold text-blue-400 mt-2">
            {weather.humidity}%
          </p>
        </div>

        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">Wind</p>
          <p className="text-2xl font-bold text-slate-200 mt-2">
            {weather.wind_mph.toFixed(1)} mph
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {weather.wind_speed.toFixed(1)} m/s
          </p>
        </div>

        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">
            {weather.is_raining ? "Rain" : "Precipitation"}
          </p>
          <p className="text-2xl font-bold text-blue-500 mt-2">
            {weather.rain_1h.toFixed(1)} mm
          </p>
          <p className="text-xs text-slate-500 mt-1">
            {weather.is_raining ? "🌧️ Raining" : "No rain"}
          </p>
        </div>

        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide">
            Location
          </p>
          <p className="text-sm font-semibold text-slate-200 mt-2">
            {weather.latitude.toFixed(2)}°N
            <br />
            {weather.longitude.toFixed(2)}°E
          </p>
        </div>
      </div>
    </div>
  );
}
