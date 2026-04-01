from typing import Any, Iterable, List


class PluginPipeline:
    """Small plugin pipeline that applies optional hooks in order."""

    def __init__(self, plugins: Iterable[Any]):
        self.plugins: List[Any] = list(plugins)

    def _run_hook(self, hook_name: str, value: Any) -> Any:
        current = value
        for plugin in self.plugins:
            hook = getattr(plugin, hook_name, None)
            if callable(hook):
                current = hook(current)
        return current

    def process_task_text(self, text: str) -> str:
        return self._run_hook("process_task_text", text)

    def process_city(self, city: str) -> str:
        return self._run_hook("process_city", city)

    def process_task(self, task: Any) -> Any:
        return self._run_hook("process_task", task)

    def process_weather(self, weather: Any) -> Any:
        return self._run_hook("process_weather", weather)

    def process_score(self, score_result: Any) -> Any:
        return self._run_hook("process_score", score_result)
