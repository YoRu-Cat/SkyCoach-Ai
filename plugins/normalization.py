import re


class InputNormalizationPlugin:
    """Normalize user text and city values before processing."""

    def process_task_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        compact = re.sub(r"\s+", " ", text).strip()
        return compact

    def process_city(self, city: str) -> str:
        if not isinstance(city, str):
            return city
        return re.sub(r"\s+", " ", city).strip()
