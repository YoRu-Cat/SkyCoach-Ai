import type { WeatherData } from "@app-types/api";

interface WeatherBackgroundProps {
  weather?: WeatherData | null;
}

const weatherTheme = (condition?: string) => {
  if (!condition) {
    return {
      base: "from-slate-950 via-slate-900 to-slate-800",
      orbA: "from-cyan-500/35 to-sky-500/5",
      orbB: "from-blue-500/20 to-indigo-500/5",
      fog: "from-white/5 via-transparent to-transparent",
    };
  }

  switch (condition) {
    case "Clear":
      return {
        base: "from-sky-900 via-cyan-900/80 to-slate-900",
        orbA: "from-amber-400/35 to-orange-400/5",
        orbB: "from-cyan-400/25 to-blue-500/5",
        fog: "from-white/10 via-transparent to-transparent",
      };
    case "Rain":
    case "Drizzle":
      return {
        base: "from-slate-950 via-blue-950 to-slate-900",
        orbA: "from-blue-500/35 to-cyan-500/5",
        orbB: "from-indigo-500/30 to-slate-700/5",
        fog: "from-slate-300/10 via-transparent to-transparent",
      };
    case "Thunderstorm":
      return {
        base: "from-black via-slate-950 to-indigo-950",
        orbA: "from-violet-500/35 to-cyan-400/5",
        orbB: "from-indigo-500/30 to-slate-800/5",
        fog: "from-white/10 via-transparent to-transparent",
      };
    case "Snow":
      return {
        base: "from-slate-900 via-sky-950 to-slate-800",
        orbA: "from-sky-200/25 to-white/5",
        orbB: "from-cyan-200/25 to-blue-500/5",
        fog: "from-white/15 via-transparent to-transparent",
      };
    default:
      return {
        base: "from-slate-950 via-slate-900 to-slate-800",
        orbA: "from-cyan-500/35 to-sky-500/5",
        orbB: "from-blue-500/20 to-indigo-500/5",
        fog: "from-white/5 via-transparent to-transparent",
      };
  }
};

export default function WeatherBackground({ weather }: WeatherBackgroundProps) {
  const theme = weatherTheme(weather?.condition);

  return (
    <div className="fixed inset-0 pointer-events-none -z-10 overflow-hidden">
      <div className={`absolute inset-0 bg-gradient-to-br ${theme.base}`} />

      <div
        className={`absolute -top-24 -left-28 w-[32rem] h-[32rem] rounded-full bg-gradient-to-br ${theme.orbA} blur-3xl weather-orb-a`}
      />
      <div
        className={`absolute -bottom-24 -right-24 w-[28rem] h-[28rem] rounded-full bg-gradient-to-tr ${theme.orbB} blur-3xl weather-orb-b`}
      />
      <div
        className={`absolute inset-0 bg-gradient-to-b ${theme.fog} weather-fog`}
      />
    </div>
  );
}