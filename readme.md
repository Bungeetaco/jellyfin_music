# Jellyfin Music Organizer

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://github.com/yourusername/jellyfin_music_organizer/workflows/Tests/badge.svg)](https://github.com/yourusername/jellyfin_music_organizer/actions)

A Python application for organizing music files based on their metadata, designed to work with Jellyfin media server. This is an enhanced fork of [ImKyleDouglas's Jellyfin Music Organizer](https://github.com/ImKyleDouglas/jellyfin_music).

## Improvements Over Original
- Complete rewrite with modern Python practices and type hints
- Enhanced error handling and detailed logging system
- Expanded audio format support
- Customizable organization rules
- Dark theme UI with better user feedback
- Progress tracking with detailed status updates
- Configuration management system
- Comprehensive test suite
- Extensive documentation
- Cross-platform support (Windows, Linux, Mac)

## Features

- **Smart Organization**: Automatically organizes music files based on metadata (artist, album, etc.)
- **Wide Format Support**: Works with most popular audio formats
- **User-Friendly**: Dark theme UI with progress tracking
- **Customizable**: Flexible organization rules to match your needs
- **Reliable**: Built-in error handling and detailed logging

## Supported Audio Formats

- AIFF/AIF (.aif, .aiff)
- APE (.ape)
- FLAC (.flac)
- M4A/M4B/M4R (.m4a, .m4b, .m4r)
- MP2/MP3/MP4 (.mp2, .mp3, .mp4)
- MPC (.mpc)
- OGG (.ogg)
- OPUS (.opus)
- WAV (.wav)
- WMA (.wma)

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- PyQt5
- mutagen
- qdarkstyle

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/jellyfin_music_organizer.git
cd jellyfin_music_organizer
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
# Basic installation
pip install -r requirements.txt

# Development installation (includes testing tools)
pip install -r requirements-dev.txt
```

### Usage

1. Run the application:
```bash
python -m jellyfin_music_organizer.main
```

2. Select your music source folder
3. Choose the destination folder
4. Configure organization settings if needed
5. Click "Organize" to start the process

The program will create a folder structure like this:

## 📖 Documentation

- [User Guide](docs/USER_GUIDE.md) - Detailed instructions for using the application
- [Development Guide](docs/DEVELOPMENT.md) - Information for developers
- [API Documentation](docs/API.md) - API reference
- [Changelog](CHANGELOG.md) - Version history and changes

## ⚙️ Configuration

Configuration files are stored in:
- Windows: `%USERPROFILE%\.jellyfin_music_organizer\config.json`
- Linux/Mac: `~/.jellyfin_music_organizer/config.json`

Logs are stored in:
- Windows: `%USERPROFILE%\.jellyfin_music_organizer\app.log`
- Linux/Mac: `~/.jellyfin_music_organizer/app.log`

## 🧪 Development

### Project Structure

```
jellyfin_music_organizer/
├── core/           # Core functionality
├── ui/            # User interface components
├── utils/         # Utility functions
└── main.py        # Application entry point
```

### Running Tests

```bash
python -m pytest tests/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the [User Guide](docs/USER_GUIDE.md)
2. Look through existing [Issues](../../issues)
3. Create a new [Issue](../../issues/new)

## Acknowledgments

- Original project by [ImKyleDouglas](https://github.com/ImKyleDouglas/jellyfin_music)
- All contributors to the original project 

## Security

- All file operations are validated and sanitized
- No external network connections required
- Local configuration storage only
- Secure file handling with integrity checks 