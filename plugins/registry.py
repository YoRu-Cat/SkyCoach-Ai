from plugins.normalization import InputNormalizationPlugin
from plugins.quality import ScoreSafetyPlugin


def get_default_plugins():
    """Return default plugins used by the runtime pipeline."""
    return [
        InputNormalizationPlugin(),
        ScoreSafetyPlugin(),
    ]
