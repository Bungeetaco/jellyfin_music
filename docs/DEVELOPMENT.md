# Jellyfin Music Organizer Development Guide

## Development Environment Setup

### Prerequisites
- Python 3.8 or higher
- Git
- A code editor (recommended: VS Code or PyCharm)
- Virtual environment tool (recommended: venv or conda)

### Setting Up the Development Environment
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/jellyfin_music_organizer.git
   cd jellyfin_music_organizer
   ```

2. Create and activate a virtual environment:
   ```bash
   # Using venv
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Or using conda
   conda create -n jellyfin_music_organizer python=3.8
   conda activate jellyfin_music_organizer
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Install the package in development mode:
   ```bash
   pip install -e .
   ```

## Project Structure
```
jellyfin_music_organizer/
├── core/           # Core functionality
│   ├── __init__.py
│   ├── organize_thread.py
│   └── notification_audio_thread.py
├── ui/             # User interface
│   ├── __init__.py
│   ├── main_window.py
│   └── custom_dialog.py
├── utils/          # Utility functions
│   ├── __init__.py
│   ├── config.py
│   ├── resources.py
│   ├── progress.py
│   ├── threads.py
│   ├── performance.py
│   └── security.py
├── resources/      # Application resources
│   ├── icons/
│   └── sounds/
├── tests/          # Test files
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_resources.py
│   ├── test_progress.py
│   └── test_threads.py
├── docs/           # Documentation
│   ├── README.md
│   ├── API.md
│   ├── USER_GUIDE.md
│   └── DEVELOPMENT.md
├── setup.py        # Package setup
├── requirements.txt
└── requirements-dev.txt
```

## Code Style and Standards

### Python Style Guide
- Follow PEP 8 guidelines
- Use type hints for all function parameters and return values
- Write docstrings for all classes and methods
- Keep functions focused and single-purpose
- Use meaningful variable and function names

### Documentation Standards
- Write clear and concise docstrings
- Include examples in complex function documentation
- Keep documentation up to date with code changes
- Use proper markdown formatting in documentation files

### Testing Standards
- Write unit tests for all new functionality
- Maintain test coverage above 80%
- Use meaningful test names
- Follow the Arrange-Act-Assert pattern

## Development Workflow

### Starting a New Feature
1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Implement your changes:
   - Write the code
   - Add tests
   - Update documentation
   - Run tests and linting

3. Commit your changes:
   ```bash
   git add .
   git commit -m "feat: description of your changes"
   ```

4. Push to your branch:
   ```bash
   git push origin feature/your-feature-name
   ```

5. Create a pull request

### Code Review Process
1. Ensure all tests pass
2. Check code coverage
3. Verify documentation is updated
4. Review code style and standards
5. Test the changes manually
6. Approve or request changes

### Release Process
1. Update version in `setup.py`
2. Update changelog
3. Create a release branch
4. Run all tests
5. Build and test the package
6. Create a GitHub release
7. Merge to main branch

## Testing

### Running Tests
```bash
# Run all tests
python -m unittest discover tests

# Run specific test file
python -m unittest tests/test_config.py

# Run with coverage
coverage run -m unittest discover tests
coverage report
```

### Writing Tests
```python
import unittest
from jellyfin_music_organizer.utils.config import ConfigManager

class TestConfigManager(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.config = ConfigManager("test_config.json")

    def test_default_config(self):
        """Test default configuration values."""
        self.assertEqual(self.config.get("version"), "3.06")

    def test_save_load_config(self):
        """Test saving and loading configuration."""
        self.config.set("test_key", "test_value")
        self.config.save()
        new_config = ConfigManager("test_config.json")
        new_config.load()
        self.assertEqual(new_config.get("test_key"), "test_value")

    def tearDown(self):
        """Clean up test fixtures."""
        import os
        if os.path.exists("test_config.json"):
            os.remove("test_config.json")
```

## Performance Optimization

### Caching
- Use the `CacheManager` for frequently accessed data
- Implement appropriate cache invalidation
- Monitor cache hit rates

### Batch Processing
- Use the `BatchProcessor` for large datasets
- Implement appropriate batch sizes
- Monitor memory usage

### Threading
- Use the `ThreadManager` for concurrent operations
- Implement proper thread synchronization
- Handle thread cleanup

## Security Considerations

### File Operations
- Validate all file paths
- Use secure file deletion
- Implement proper error handling

### Input Validation
- Validate all user input
- Sanitize file paths
- Check file permissions

### Error Handling
- Use custom exceptions
- Implement proper logging
- Provide user-friendly error messages

## Debugging

### Logging
```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
```

### Debug Tools
- Use Python debugger (pdb)
- Implement logging statements
- Use IDE debugging features

## Contributing Guidelines

### Pull Request Process
1. Update documentation
2. Add tests
3. Follow code style
4. Provide clear description
5. Link related issues

### Code Review Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code style followed
- [ ] No new dependencies
- [ ] Error handling implemented
- [ ] Performance considered
- [ ] Security checked

## Release Management

### Versioning
Follow semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Changelog
Keep a detailed changelog:
```markdown
# Changelog

## [3.06] - 2024-03-21
### Added
- New feature X
- New feature Y

### Changed
- Updated feature Z
- Improved performance

### Fixed
- Bug in feature A
- Issue with feature B
```

## Support and Maintenance

### Issue Management
- Use GitHub issues
- Follow issue templates
- Provide reproduction steps
- Include system information

### Documentation Updates
- Keep documentation current
- Update examples
- Add troubleshooting guides
- Maintain API documentation

## License
This project is licensed under the MIT License. See the LICENSE file for details. 