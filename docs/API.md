# Jellyfin Music Organizer API Documentation

## Core Components

### ConfigManager
Manages application configuration and settings.

```python
class ConfigManager:
    def __init__(self, config_file: str = "config.json")
    def get(self, key: str, default: Any = None) -> Any
    def set(self, key: str, value: Any) -> None
    def save(self) -> None
    def load(self) -> None
```

### ResourceManager
Manages application resources and file paths.

```python
class ResourceManager:
    def __init__(self, base_path: Optional[str] = None)
    def register_resource(self, name: str, path: str) -> None
    def get_resource_path(self, name: str) -> str
    def get_resource_content(self, name: str) -> bytes
    def get_resource_text(self, name: str) -> str
    def validate_resources(self) -> bool
```

### ProgressTracker
Tracks progress of long-running operations.

```python
class ProgressTracker:
    def __init__(self, total: int, callback: Optional[Callable[[ProgressInfo], None]] = None)
    def update(self, current: int, current_item: Optional[str] = None, status: Optional[str] = None) -> None
    def increment(self) -> None
    def get_progress_info(self) -> ProgressInfo
    def get_percentage(self) -> float
    def get_elapsed_time(self) -> float
    def get_estimated_time_remaining(self) -> float
```

### ThreadManager
Manages application threads and communication.

```python
class ThreadManager:
    def __init__(self)
    def start_thread(self, name: str, target: Callable, args: tuple = (), kwargs: dict = None) -> None
    def stop_thread(self, name: str) -> None
    def stop_all_threads(self) -> None
    def get_thread_status(self, name: str) -> Optional[Dict[str, Any]]
    def get_thread_message(self, name: str) -> Optional[Tuple[str, Any]]
    def is_thread_running(self, name: str) -> bool
```

## Performance Utilities

### CacheManager
Manages caching for frequently accessed data.

```python
class CacheManager:
    def __init__(self, max_size: int = 1000)
    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any) -> None
    def invalidate(self, key: str) -> None
    def clear(self) -> None
```

### BatchProcessor
Processes items in batches for better performance.

```python
class BatchProcessor:
    def __init__(self, items: List[Any], batch_size: int = 100)
    def process(self, processor: Callable[[Any], None]) -> None
    def process_with_progress(self, processor: Callable[[Any], None], progress_callback: Optional[Callable[[int, int], None]] = None) -> None
```

### PerformanceMonitor
Monitors application performance.

```python
class PerformanceMonitor:
    def __init__(self)
    def start_operation(self, name: str) -> None
    def end_operation(self, name: str) -> None
    def get_operation_stats(self, name: str) -> Dict[str, Any]
    def get_memory_usage(self) -> float
    def log_performance_metrics(self) -> None
```

## Security Utilities

### SecurityManager
Manages security-related operations.

```python
class SecurityManager:
    def __init__(self)
    def validate_file_permissions(self, file_path: str, required_permissions: int) -> bool
    def secure_delete(self, file_path: str) -> None
    def validate_path(self, path: str) -> bool
    def sanitize_path(self, path: str) -> str
    def calculate_file_hash(self, file_path: str, algorithm: str = "sha256") -> Optional[str]
    def verify_file_integrity(self, file_path: str, expected_hash: str) -> bool
```

## UI Components

### MainWindow
Main application window.

```python
class MainWindow(QMainWindow):
    def __init__(self)
    def setup_ui(self) -> None
    def setup_connections(self) -> None
    def load_settings(self) -> None
    def save_settings(self) -> None
    def show_error(self, message: str) -> None
    def show_success(self, message: str) -> None
```

### CustomDialog
Custom dialog window for messages.

```python
class CustomDialog(QDialog):
    def __init__(self, custom_message: str)
    def center_window(self) -> None
    def showEvent(self, event: QShowEvent) -> None
    def closeEvent(self, event: QCloseEvent) -> None
    def load_settings(self) -> None
```

## Threads

### OrganizeThread
Thread for organizing music files.

```python
class OrganizeThread(QThread):
    def __init__(self, settings: Dict[str, str])
    def run(self) -> None
    def stop(self) -> None
```

### NotificationAudioThread
Thread for playing notification sounds.

```python
class NotificationAudioThread(QThread):
    def __init__(self, audio_file_name: str)
    def run(self) -> None
    def on_media_status_changed(self, status: QMediaPlayer.MediaStatus) -> None
```

## Error Handling

### FileOperationError
Exception raised for file operation errors.

```python
class FileOperationError(Exception):
    def __init__(self, message: str, file_path: Optional[str] = None)
```

## Constants

### Supported Audio Formats
```python
SUPPORTED_AUDIO_FORMATS = [
    ".mp3", ".m4a", ".flac", ".wav", ".ogg", ".wma", ".aac"
]
```

### Default Settings
```python
DEFAULT_SETTINGS = {
    "music_folder": "",
    "destination_folder": "",
    "mute_sound": False,
    "version": "3.06"
}
``` 