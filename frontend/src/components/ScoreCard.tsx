import type { SkyScoreResult } from "@app-types/api";
import ScoreGauge from "@components/ScoreGauge";

interface ScoreCardProps {
  score: SkyScoreResult;
}

const getScoreColor = (score: number): string => {
  if (score >= 80) return "text-green-400";
  if (score >= 60) return "text-cyan-400";
  if (score >= 40) return "text-yellow-400";
  return "text-red-400";
};

const getScoreBackground = (score: number): string => {
  if (score >= 80) return "from-green-600 to-green-400";
  if (score >= 60) return "from-cyan-600 to-cyan-400";
  if (score >= 40) return "from-yellow-600 to-yellow-400";
  return "from-red-600 to-red-400";
};

const getScoreLabel = (score: number): string => {
  if (score >= 80) return "Perfect!";
  if (score >= 60) return "Go for it!";
  if (score >= 40) return "Possible";
  return "Not ideal";
};

export default function ScoreCard({ score }: ScoreCardProps) {
  return (
    <div className="card space-y-6 glow-cyan">
      <div className="text-center">
        <h3 className="text-lg font-bold text-slate-100 mb-4">📊 SkyScore</h3>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 items-center mb-6">
          <ScoreGauge score={score.score} />

          <div className="text-left sm:pl-2">
            <p className={`text-3xl font-bold ${getScoreColor(score.score)}`}>
              {getScoreLabel(score.score)}
            </p>
            <p className="text-sm text-slate-400 mt-2">
              {score.classification} activity conditions
            </p>
            <p className="text-xs text-slate-500 mt-2">
              Needle and segments animate based on real weather score.
            </p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className={`h-full bg-gradient-to-r ${getScoreBackground(score.score)}`}
            style={{ width: `${score.score}%` }}
          />
        </div>
      </div>

      {/* Recommendation */}
      <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
        <p className="text-sm text-slate-300">{score.recommendation}</p>
      </div>

      {/* Factors */}
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
                    <p className="text-xs text-slate-400">{bonus.description}</p>
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
                    <p className="text-xs text-slate-400">{penalty.description}</p>
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
