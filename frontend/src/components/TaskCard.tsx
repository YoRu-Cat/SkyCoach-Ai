import type { TaskAnalysis } from "@app-types/api";

interface TaskCardProps {
  task: TaskAnalysis;
  onUseSuggestion?: (value: string) => void;
}

export default function TaskCard({ task, onUseSuggestion }: TaskCardProps) {
  const getClassificationColor = (classification: string) => {
    return classification === "Outdoor" ? "text-amber-400" : "text-blue-400";
  };

  const confidenceSegments = 20;
  const filledConfidenceSegments = Math.round(
    task.confidence * confidenceSegments,
  );

  return (
    <div className="card space-y-4 glow-cyan">
      <div className="flex items-start justify-between mb-4 gap-3">
        <h3 className="text-lg font-bold text-slate-100">
          🧠 Activity Analysis
        </h3>
        <span
          className={`text-sm font-semibold ${getClassificationColor(task.classification)}`}>
          {task.classification}
        </span>
      </div>

      {task.needs_clarification && (
        <div className="p-3 bg-yellow-900/30 border border-yellow-600/50 rounded-lg">
          <p className="text-sm text-yellow-300">
            ⚠️ {task.issue || "Input needs clarification"}
          </p>
        </div>
      )}

      <div className="space-y-3">
        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            Original Input
          </label>
          <p className="text-slate-200 mt-1">
            &quot;{task.original_text}&quot;
          </p>
        </div>

        <div>
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
            Identified Activity
          </label>
          <p className="text-slate-200 mt-1">
            {task.activity === "Needs clarification" ? (
              <span className="text-yellow-400">{task.activity}</span>
            ) : (
              task.activity
            )}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
              Confidence
            </label>
            <div className="mt-2 flex items-center gap-2">
              <div className="flex-1 score-meter">
                {Array.from({ length: confidenceSegments }, (_, index) => (
                  <span
                    key={index}
                    className={`score-meter__segment ${index < filledConfidenceSegments ? "is-active" : ""}`}
                  />
                ))}
              </div>
              <span className="text-sm font-semibold text-slate-200">
                {Math.round(task.confidence * 100)}%
              </span>
            </div>
          </div>

          {task.reasoning && (
            <div>
              <label className="text-xs font-semibold text-slate-400 uppercase tracking-wide">
                Reasoning
              </label>
              <p className="text-xs text-slate-300 mt-2">{task.reasoning}</p>
            </div>
          )}
        </div>
      </div>

      {task.suggested_activity && (
        <div className="pt-4 border-t border-slate-700">
          <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3">
            <p className="text-xs font-semibold text-cyan-400 uppercase tracking-wide mb-2">
              💡 Auto-Judge Suggestion
            </p>
            <div className="space-y-2">
              <div>
                <p className="text-xs text-slate-400">Likely activity</p>
                <p className="text-slate-200 font-semibold">
                  {task.suggested_activity}
                </p>
              </div>
              <div className="flex gap-4">
                <div>
                  <p className="text-xs text-slate-400">Classification</p>
                  <p
                    className={`font-semibold ${getClassificationColor(task.suggested_classification || "")}`}>
                    {task.suggested_classification}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-400">Confidence</p>
                  <p className="text-slate-200 font-semibold">
                    {Math.round(task.suggestion_confidence * 100)}%
                  </p>
                </div>
              </div>
              {onUseSuggestion && (
                <button
                  type="button"
                  onClick={() =>
                    task.suggested_activity &&
                    onUseSuggestion(task.suggested_activity)
                  }
                  className="mt-2 px-3 py-1.5 text-xs rounded-lg bg-cyan-500/20 border border-cyan-400/40 text-cyan-200 hover:bg-cyan-500/30 transition-colors">
                  Use suggestion and re-analyze
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
