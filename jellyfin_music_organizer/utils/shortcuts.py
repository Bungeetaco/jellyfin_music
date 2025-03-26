"""Platform-specific keyboard shortcuts."""

import platform
from typing import Dict

from PyQt5.QtCore import Qt


class ShortcutManager:
    """Manage platform-specific keyboard shortcuts."""

    @staticmethod
    def get_shortcuts() -> Dict[str, str]:
        """Get platform-specific keyboard shortcuts.

        Returns:
            Dictionary of action names to shortcut keys
        """
        is_mac = platform.system() == "Darwin"

        return {
            "copy": "Cmd+C" if is_mac else "Ctrl+C",
            "paste": "Cmd+V" if is_mac else "Ctrl+V",
            "save": "Cmd+S" if is_mac else "Ctrl+S",
            "quit": "Cmd+Q" if is_mac else "Alt+F4",
            "settings": "Cmd+," if is_mac else "Ctrl+P",
            "refresh": "Cmd+R" if is_mac else "F5",
        }

    @staticmethod
    def get_modifier_key() -> Qt.KeyboardModifier:
        """Get platform-specific modifier key.

        Returns:
            Qt modifier key constant
        """
        if platform.system() == "Darwin":
            return Qt.KeyboardModifier.MetaModifier
        return Qt.KeyboardModifier.ControlModifier


def get_platform_modifier() -> Qt.KeyboardModifier:
    """Get the platform-specific modifier key.

    Returns:
        Qt modifier key constant
    """
    if platform.system() == "Darwin":
        return Qt.KeyboardModifier.MetaModifier
    return Qt.KeyboardModifier.ControlModifier
