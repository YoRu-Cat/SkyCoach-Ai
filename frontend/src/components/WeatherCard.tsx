import type { WeatherData } from "@app-types/api";

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
  const latLabel = `${Math.abs(weather.latitude).toFixed(2)}°${weather.latitude >= 0 ? "N" : "S"}`;
  const lonLabel = `${Math.abs(weather.longitude).toFixed(2)}°${weather.longitude >= 0 ? "E" : "W"}`;
  const mapSrc = `https://www.openstreetmap.org/export/embed.html?bbox=${weather.longitude - 0.18}%2C${weather.latitude - 0.12}%2C${weather.longitude + 0.18}%2C${weather.latitude + 0.12}&layer=mapnik&marker=${weather.latitude}%2C${weather.longitude}`;

  return (
    <div className="card glow-cyan space-y-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-100">
          {getWeatherEmoji(weather.condition)} Weather
        </h3>
        <p className="text-sm text-slate-400">
          {weather.city}, {weather.country}
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="px-3 py-1 text-xs rounded-full bg-cyan-500/15 border border-cyan-400/30 text-cyan-200">
          {weather.condition}
        </span>
        <span className="px-3 py-1 text-xs rounded-full bg-blue-500/15 border border-blue-400/30 text-blue-200">
          Wind {weather.wind_mph.toFixed(1)} mph
        </span>
        <span className="px-3 py-1 text-xs rounded-full bg-emerald-500/15 border border-emerald-400/30 text-emerald-200">
          Humidity {weather.humidity}%
        </span>
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
            {latLabel}
            <br />
            {lonLabel}
          </p>
        </div>
      </div>

      <div className="rounded-xl overflow-hidden border border-slate-700/70 bg-slate-900/50">
        <div className="px-3 py-2 border-b border-slate-700/70 text-xs text-slate-400 uppercase tracking-wide">
          Map Preview
        </div>
        <iframe
          title="Location map"
          src={mapSrc}
          className="w-full h-56"
          loading="lazy"
        />
      </div>
    </div>
  );
}
