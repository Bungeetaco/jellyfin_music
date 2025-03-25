# Jellyfin Music Organizer Documentation

## Overview
Jellyfin Music Organizer is a Python application that helps organize music files based on their metadata. It provides a user-friendly interface for selecting source and destination folders, and automatically organizes music files into artist and album folders.

## Features
- Automatic music file organization
- Metadata-based folder structure
- Progress tracking
- Error handling and reporting
- Customizable settings
- Secure file operations

## Installation

### Requirements
- Python 3.8 or higher
- PyQt5
- mutagen
- qdarkstyle

### Installation Steps
1. Clone the repository:
```bash
git clone https://github.com/yourusername/jellyfin_music_organizer.git
cd jellyfin_music_organizer
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python -m jellyfin_music_organizer
```

## Usage

### Basic Usage
1. Launch the application
2. Select your music source folder
3. Select your destination folder
4. Click "Organize" to start the process

### Settings
- **Music Folder**: Source folder containing music files
- **Destination Folder**: Where organized files will be saved
- **Mute Sound**: Disable notification sounds
- **Version**: Application version information

### File Organization
Files are organized in the following structure:
```
Destination/
  Artist/
    Album/
      song1.mp3
      song2.mp3
      ...
```

## Development

### Project Structure
```
jellyfin_music_organizer/
├── core/           # Core functionality
├── ui/             # User interface
├── utils/          # Utility functions
├── resources/      # Application resources
└── tests/          # Test files
```

### Adding New Features
1. Create a new branch for your feature
2. Implement the feature
3. Add tests
4. Update documentation
5. Submit a pull request

### Running Tests
```bash
python -m unittest discover tests
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Support
For support, please open an issue in the GitHub repository or contact the maintainers.

## Acknowledgments
- PyQt5 for the GUI framework
- mutagen for audio file metadata handling
- qdarkstyle for the dark theme 