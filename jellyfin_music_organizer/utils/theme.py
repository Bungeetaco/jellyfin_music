import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class ThemeColors:
    """Theme color definitions."""

    primary: str
    secondary: str
    background: str
    text: str
    error: str
    warning: str
    success: str


@dataclass
class ThemeDimensions:
    """Theme dimension definitions."""

    padding: int
    margin: int
    border_radius: int
    icon_size: int


class Theme:
    """Theme configuration."""

    def __init__(self, colors: ThemeColors, dimensions: ThemeDimensions) -> None:
        self.colors = colors
        self.dimensions = dimensions

    def get_style(self, widget_type: str) -> str:
        """Get style for a specific widget type."""
        styles = {
            "window": f"""
                QWidget {{
                    background-color: {self.colors.background};
                    color: {self.colors.text};
                    border-radius: {self.dimensions.border_radius}px;
                }}
            """,
            "button": f"""
                QPushButton {{
                    background-color: {self.colors.primary};
                    color: {self.colors.text};
                    padding: {self.dimensions.padding}px;
                    border-radius: {self.dimensions.border_radius}px;
                }}
                QPushButton:hover {{
                    background-color: {self.colors.secondary};
                }}
            """,
        }
        return styles.get(widget_type, "")


class ThemeManager:
    """Manage application themes."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._themes: Dict[str, Theme] = {}
        self._current_theme: Optional[str] = None

    def load_theme(self, theme_file: Path) -> bool:
        """Load a theme from a JSON file."""
        try:
            with open(theme_file, "r", encoding="utf-8") as f:
                theme_data = json.load(f)

            colors = ThemeColors(**theme_data["colors"])
            dimensions = ThemeDimensions(**theme_data["dimensions"])

            theme_name = theme_file.stem
            self._themes[theme_name] = Theme(colors, dimensions)
            return True
        except Exception as e:
            self.logger.error(f"Failed to load theme {theme_file}: {e}")
            return False

    def apply_theme(self, theme_name: str) -> bool:
        """Apply a theme to the application."""
        if theme_name not in self._themes:
            return False

        self._current_theme = theme_name
        return True

    def get_current_theme(self) -> Optional[Theme]:
        """Get the current theme."""
        if self._current_theme:
            return self._themes.get(self._current_theme)
        return None
