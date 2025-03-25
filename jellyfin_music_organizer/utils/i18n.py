import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional


class I18n:
    """Internationalization support."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self._translations: Dict[str, Dict[str, str]] = {}
        self._current_locale = "en"
        self._fallback_locale = "en"

    def load_translations(self, locale_dir: Path) -> None:
        """Load all translation files from directory."""
        try:
            for file_path in locale_dir.glob("*.json"):
                locale = file_path.stem
                with open(file_path, "r", encoding="utf-8") as f:
                    self._translations[locale] = json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load translations: {e}")

    def set_locale(self, locale: str) -> bool:
        """Set the current locale."""
        if locale in self._translations:
            self._current_locale = locale
            return True
        return False

    def get_text(self, key: str, locale: Optional[str] = None, **kwargs: Any) -> str:
        """Get translated text."""
        try:
            # Use specified locale or current locale
            current = locale or self._current_locale

            # Try current locale
            if current in self._translations:
                text = self._translations[current].get(key)
                if text is not None:
                    return text.format(**kwargs)

            # Try fallback locale
            if self._fallback_locale in self._translations:
                text = self._translations[self._fallback_locale].get(key)
                if text is not None:
                    return text.format(**kwargs)

            # Return key if no translation found
            return key
        except Exception as e:
            self.logger.error(f"Translation error for key '{key}': {e}")
            return key
