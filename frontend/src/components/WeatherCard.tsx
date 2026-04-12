import type { WeatherData } from "@app-types/api";
import { CircleMarker, MapContainer, TileLayer, Tooltip } from "react-leaflet";

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
  const coordinates: [number, number] = [weather.latitude, weather.longitude];

  return (
    <div className="card space-y-5 weather-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold text-slate-100">
          {getWeatherEmoji(weather.condition)} Weather
        </h3>
        <p className="text-sm text-slate-400">
          {weather.city}, {weather.country}
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        <span className="px-3 py-1 text-xs rounded-full bg-fuchsia-500/15 border border-fuchsia-400/30 text-fuchsia-200">
          {weather.condition}
        </span>
        <span className="px-3 py-1 text-xs rounded-full bg-violet-500/15 border border-violet-400/30 text-violet-200">
          Wind {weather.wind_mph.toFixed(1)} mph
        </span>
        <span className="px-3 py-1 text-xs rounded-full bg-purple-500/15 border border-purple-400/30 text-purple-200">
          Humidity {weather.humidity}%
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <div className="p-3 bg-slate-800/50 rounded-lg">
          <p className="text-xs text-slate-400 uppercase tracking-wide weather-metric-label">
            Temperature
          </p>
          <p className="text-2xl font-bold text-fuchsia-300 mt-2 weather-metric-value">
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
          <p className="text-xs text-slate-400 uppercase tracking-wide weather-metric-label">
            Humidity
          </p>
          <p className="text-2xl font-bold text-violet-300 mt-2 weather-metric-value">
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
          <p className="text-xs text-slate-400 uppercase tracking-wide weather-metric-label">
            {weather.is_raining ? "Rain" : "Precipitation"}
          </p>
          <p className="text-2xl font-bold text-purple-300 mt-2 weather-metric-value">
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

      <div className="weather-map-shell rounded-xl overflow-hidden border border-[#a171e8]/65 bg-[#1a0d2b]/82">
        <div className="px-3 py-2 border-b border-[#a171e8]/55 text-xs text-[#f1e3ff] uppercase tracking-wide">
          Map Preview
        </div>
        <div className="weather-map-frame relative h-56 w-full overflow-hidden">
          <MapContainer
            center={coordinates}
            zoom={12}
            scrollWheelZoom={false}
            className="weather-leaflet-map h-full w-full"
            attributionControl={false}>
            <TileLayer url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png" />
            <CircleMarker
              center={coordinates}
              radius={9}
              pathOptions={{
                color: "#f5dbff",
                weight: 2,
                fillColor: "#bb4dfb",
                fillOpacity: 0.78,
              }}>
              <Tooltip direction="top" offset={[0, -8]} opacity={0.95}>
                {weather.city}, {weather.country}
              </Tooltip>
            </CircleMarker>
          </MapContainer>
          <div className="weather-map-overlay" />
          <div className="weather-map-credit">
            Map Data: OpenStreetMap, CARTO
          </div>
        </div>
      </div>
    </div>
  );
}
