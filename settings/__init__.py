from .settings import get_setting, Settings

__all__ = [
    "settings",
]

settings: Settings = get_setting()
