import type { TaskAnalysis } from "@app-types/api";

interface TaskCardProps {
  task: TaskAnalysis;
  onUseSuggestion?: (value: string) => void;
  onAddToTodo?: (payload: {
    title: string;
    notes?: string;
    scheduledAt?: string;
    category?: "indoor" | "outdoor";
  }) => void;
}

export default function TaskCard({
  task,
  onUseSuggestion,
  onAddToTodo,
}: TaskCardProps) {
  const extractScheduleTime = (value?: string) => {
    if (!value) return undefined;
    const match = value.match(/\b(\d{1,2}:\d{2})\b/);
    return match?.[1];
  };

  const suggestionText = task.suggested_activity?.trim() || "";
  const hasActionableSuggestion =
    suggestionText.length > 0 &&
    suggestionText.toLowerCase() !== task.activity.toLowerCase() &&
    suggestionText.toLowerCase() !== task.original_text.toLowerCase();
  const hasAlternateClassificationSuggestion =
    !!task.suggested_classification &&
    task.suggestion_confidence >= 0.55 &&
    task.suggested_classification !== task.classification;
  const showSuggestionPanel =
    hasActionableSuggestion || hasAlternateClassificationSuggestion;

  const getClassificationColor = (classification: string) => {
    return classification === "Outdoor"
      ? "task-classification task-classification-outdoor"
      : "task-classification task-classification-indoor";
  };

  const confidenceSegments = 20;
  const filledConfidenceSegments = Math.round(
    task.confidence * confidenceSegments,
  );
  const bestScheduledAt =
    task.best_date && extractScheduleTime(task.best_time)
      ? `${task.best_date}T${extractScheduleTime(task.best_time)}:00`
      : undefined;
  const todoTitle =
    task.suggested_activity?.trim() || task.activity || task.original_text;
  const todoCategory = task.classification === "Outdoor" ? "outdoor" : "indoor";
  const todoNotes = task.best_datetime_reason || task.reasoning;

  return (
    <div className="card space-y-4">
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

      {showSuggestionPanel && (
        <div className="pt-4 border-t border-slate-700">
          <div className="bg-fuchsia-500/10 border border-fuchsia-400/30 rounded-lg p-3">
            <p className="text-xs font-semibold text-fuchsia-300 uppercase tracking-wide mb-2">
              💡 Auto-Judge Suggestion
            </p>
            <div className="space-y-2">
              {hasActionableSuggestion && task.suggested_activity && (
                <div>
                  <p className="text-xs text-slate-400">Likely activity</p>
                  <p className="text-slate-200 font-semibold">
                    {task.suggested_activity}
                  </p>
                </div>
              )}
              <div className="flex gap-4">
                {hasAlternateClassificationSuggestion &&
                  task.suggested_classification && (
                    <div>
                      <p className="text-xs text-slate-400">Did you mean</p>
                      <p
                        className={`font-semibold ${getClassificationColor(task.suggested_classification || "")}`}>
                        {task.suggested_classification}
                      </p>
                    </div>
                  )}
                <div>
                  <p className="text-xs text-slate-400">Confidence</p>
                  <p className="text-slate-200 font-semibold">
                    {Math.round(task.suggestion_confidence * 100)}%
                  </p>
                </div>
              </div>
              {onUseSuggestion && hasActionableSuggestion && (
                <button
                  type="button"
                  onClick={() => onUseSuggestion(suggestionText)}
                  className="mt-2 px-3 py-1.5 text-xs rounded-lg bg-fuchsia-500/20 border border-fuchsia-400/40 text-fuchsia-200 hover:bg-fuchsia-500/30 transition-colors">
                  Use suggestion and re-analyze
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {(task.best_date || task.best_time) && (
        <div className="pt-4 border-t border-slate-700">
          <div className="bg-violet-500/10 border border-violet-400/30 rounded-lg p-3">
            <p className="text-xs font-semibold text-violet-300 uppercase tracking-wide mb-2">
              🗓️ Best Time Suggestion
            </p>
            <div className="flex flex-wrap gap-4 text-sm">
              {task.best_date && (
                <div>
                  <p className="text-xs text-slate-400">Date</p>
                  <p className="text-slate-200 font-semibold">
                    {task.best_date}
                  </p>
                </div>
              )}
              {task.best_time && (
                <div>
                  <p className="text-xs text-slate-400">Time</p>
                  <p className="text-slate-200 font-semibold">
                    {task.best_time}
                  </p>
                </div>
              )}
            </div>
            {task.best_datetime_reason && (
              <p className="text-xs text-slate-300 mt-2">
                {task.best_datetime_reason}
              </p>
            )}
            {onAddToTodo && bestScheduledAt && (
              <button
                type="button"
                onClick={() =>
                  onAddToTodo({
                    title: todoTitle,
                    notes: todoNotes,
                    scheduledAt: bestScheduledAt,
                    category: todoCategory,
                  })
                }
                className="mt-3 px-3 py-1.5 text-xs rounded-lg bg-violet-500/20 border border-violet-400/40 text-violet-100 hover:bg-violet-500/30 transition-colors">
                Add best plan to Todo List
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
