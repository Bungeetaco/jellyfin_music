import tempfile
from pathlib import Path
from typing import Any, Dict, Generator, Optional

import pytest
from PyQt6.QtWidgets import QApplication, QWidget


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Create mock configuration."""
    return {
        "version": "1.0.0",
        "paths": {"music": "/path/to/music", "output": "/path/to/output"},
        "settings": {"organize_by": "artist", "copy_files": True},
    }


@pytest.fixture
def qt_app() -> Generator[QApplication, None, None]:
    """Create QApplication instance for testing."""
    app = QApplication([])
    yield app
    app.quit()


class MockWidget(QWidget):
    """Mock widget for testing."""

    def __init__(self) -> None:
        super().__init__()
        self.shown = False
        self.hidden = False
        self.closed = False

    def show(self) -> None:
        self.shown = True
        super().show()

    def hide(self) -> None:
        self.hidden = True
        super().hide()

    def close(self) -> None:
        self.closed = True
        super().close()


def create_mock_file(path: Path, content: str = "") -> None:
    """Create a mock file with content."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def create_mock_directory(path: Path) -> None:
    """Create a mock directory structure."""
    path.mkdir(parents=True, exist_ok=True)


class MockResponse:
    """Mock HTTP response for testing."""

    def __init__(
        self, status_code: int = 200, json_data: Optional[Dict[str, Any]] = None, text: str = ""
    ) -> None:
        self.status_code = status_code
        self._json_data = json_data or {}
        self.text = text

    def json(self) -> Dict[str, Any]:
        return self._json_data

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")
