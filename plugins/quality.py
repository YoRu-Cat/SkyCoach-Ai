class ScoreSafetyPlugin:
    """Clamp score outputs and confidence to safe bounds."""

    def process_task(self, task):
        if hasattr(task, "confidence"):
            task.confidence = max(0.0, min(1.0, float(task.confidence)))
        return task

    def process_score(self, score_result):
        if hasattr(score_result, "score"):
            score_result.score = max(0, min(100, int(score_result.score)))
        return score_result
