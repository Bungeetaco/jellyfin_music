"""Configuration for notification sounds."""


class NotificationConfig:
    """Manages notification sound configurations."""

    @staticmethod
    def get_sound(sound_type: str, platform: str) -> str:
        """Get the appropriate sound for the platform."""
        sounds = {
            "windows": {
                "alert": "SystemAsterisk",
                "error": "SystemHand",
                "complete": "SystemDefault",
            },
            "darwin": {
                "alert": "Ping",
                "error": "Basso",
                "complete": "Glass",
            },
            "linux": {
                "alert": "dialog-warning",
                "error": "dialog-error",
                "complete": "complete",
            },
        }
        return sounds.get(platform, {}).get(sound_type, "")
