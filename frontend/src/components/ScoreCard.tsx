import type { SkyScoreResult } from "@app-types/api";
import ScoreGauge from "@components/ScoreGauge";

interface ScoreCardProps {
  score: SkyScoreResult;
}

const getScoreColor = (score: number): string => {
  if (score >= 80) return "text-[#d89eff]";
  if (score >= 60) return "text-[#c07eff]";
  if (score >= 40) return "text-[#b35cf8]";
  return "text-[#9e38e8]";
};

const getScoreLabel = (score: number): string => {
  if (score >= 80) return "Perfect!";
  if (score >= 60) return "Go for it!";
  if (score >= 40) return "Possible";
  return "Not ideal";
};

export default function ScoreCard({ score }: ScoreCardProps) {
  const scorePercent = Math.max(0, Math.min(100, score.score));
  const scoreSegments = 10;
  const filledScoreSegments = Math.round(scorePercent / 10);

  return (
    <div className="card space-y-6 glow-cyan">
      <div className="relative overflow-hidden rounded-[28px] border border-[#5c0390]/45 bg-gradient-to-br from-[#11001c]/86 via-[#1c012c]/70 to-[#11001c]/48 p-5 sm:p-6">
        <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-[#bb4dfb]/70 to-transparent" />
        <div className="absolute -right-10 top-2 h-28 w-28 rounded-full bg-[#9505e9]/16 blur-3xl" />

        <div className="flex items-start gap-4 sm:gap-5">
          <div className="shrink-0 pt-1">
            <ScoreGauge score={score.score} />
          </div>

          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <p className="text-[0.68rem] uppercase tracking-[0.35em] text-slate-500">
                  SkyScore
                </p>
                <p
                  className={`mt-1 text-3xl sm:text-4xl font-semibold ${getScoreColor(score.score)} leading-tight`}>
                  {getScoreLabel(score.score)}
                </p>
              </div>

              <div className="rounded-full border border-[#5c0390]/55 bg-[#150121]/72 px-3 py-2 text-right">
                <p className="text-2xl font-semibold text-[#d89eff] leading-none">
                  {score.score}
                </p>
                <p className="mt-1 text-[0.62rem] uppercase tracking-[0.32em] text-slate-500">
                  out of 100
                </p>
              </div>
            </div>

            <p className="mt-3 text-sm text-slate-400">
              {score.classification} activity conditions
            </p>
            <p className="mt-2 max-w-xl text-sm leading-6 text-slate-500">
              A compact read on the weather balance for this activity.
            </p>

            <div className="mt-5">
              <div className="grid grid-cols-10 gap-1 rounded-full bg-slate-900/80 p-1 ring-1 ring-white/5">
                {Array.from({ length: scoreSegments }, (_, index) => (
                  <span
                    key={index}
                    className={`h-2 rounded-full transition-all duration-300 ${
                      index < filledScoreSegments
                        ? "bg-gradient-to-r from-[#9505e9] via-[#b13dff] to-[#dda6fd] shadow-[0_0_10px_rgba(149,5,233,0.42)]"
                        : "bg-[#3a015c]/68"
                    }`}
                  />
                ))}
              </div>
              <div className="mt-2 flex items-center justify-between text-[0.7rem] uppercase tracking-[0.28em] text-slate-500">
                <span>risk</span>
                <span>readiness</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <p className="text-sm text-slate-300">{score.recommendation}</p>
      </div>

      <div className="space-y-4">
        {score.bonuses.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-green-400 uppercase tracking-wide mb-3">
              ✓ Bonuses
            </p>
            <div className="space-y-2">
              {score.bonuses.map((bonus, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-start p-2 bg-green-900/20 rounded border border-green-700/30">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-green-300">
                      {bonus.name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {bonus.description}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-green-400">
                    +{bonus.value}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {score.penalties.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-red-400 uppercase tracking-wide mb-3">
              ✗ Penalties
            </p>
            <div className="space-y-2">
              {score.penalties.map((penalty, idx) => (
                <div
                  key={idx}
                  className="flex justify-between items-start p-2 bg-red-900/20 rounded border border-red-700/30">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-red-300">
                      {penalty.name}
                    </p>
                    <p className="text-xs text-slate-400">
                      {penalty.description}
                    </p>
                  </div>
                  <span className="text-sm font-bold text-red-400">
                    {penalty.value}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Weather Factors */}
      {score.weather_factors.length > 0 && (
        <div className="pt-4 border-t border-slate-700">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wide mb-2">
            Weather Factors
          </p>
          <p className="text-sm text-slate-300">
            {score.weather_factors.join(", ")}
          </p>
        </div>
      )}
    </div>
  );
}
