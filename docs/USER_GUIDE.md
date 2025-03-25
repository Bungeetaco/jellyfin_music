# Jellyfin Music Organizer User Guide

## Introduction
Welcome to the Jellyfin Music Organizer! This guide will help you understand how to use the application to organize your music files efficiently.

## Getting Started

### Installation
1. Download the latest release from the GitHub repository
2. Install Python 3.8 or higher if you haven't already
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the application:
   ```bash
   python -m jellyfin_music_organizer
   ```

### First Launch
When you first launch the application, you'll see the main window with the following options:
- Music Folder: Select your source music folder
- Destination Folder: Select where you want the organized files to be saved
- Mute Sound: Toggle notification sounds
- Version: Shows the current version of the application

## Using the Application

### Selecting Folders
1. Click the "Browse" button next to "Music Folder" to select your source music folder
2. Click the "Browse" button next to "Destination Folder" to select where you want the organized files to be saved
3. Make sure both folders are selected before proceeding

### Organizing Music
1. Once you've selected your folders, click the "Organize" button
2. The application will start processing your music files
3. A progress bar will show the current status
4. You'll see notifications for:
   - Start of the organization process
   - Completion of the process
   - Any errors that occur

### Understanding the Organization
Your music files will be organized in the following structure:
```
Destination/
  Artist/
    Album/
      song1.mp3
      song2.mp3
      ...
```

The application uses the following metadata to organize files:
- Artist name
- Album name
- Track number (for sorting)
- Track title

### Supported File Formats
The application supports the following audio formats:
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- WAV (.wav)
- OGG (.ogg)
- WMA (.wma)
- AAC (.aac)

## Troubleshooting

### Common Issues
1. **No Music Files Found**
   - Make sure you've selected the correct source folder
   - Verify that the folder contains supported audio files
   - Check file permissions

2. **Organization Failed**
   - Ensure you have write permissions in the destination folder
   - Check if the destination folder has enough space
   - Verify that the files aren't locked by another application

3. **Missing Metadata**
   - The application will use the filename if metadata is missing
   - Consider using a metadata editor to add missing information

### Error Messages
- **"Invalid folder selected"**: The selected folder doesn't exist or isn't accessible
- **"No supported audio files found"**: The source folder doesn't contain any supported audio formats
- **"Insufficient permissions"**: The application doesn't have permission to access or modify the selected folders

## Tips and Best Practices

### Before Organizing
1. Back up your music files
2. Ensure all files have proper metadata
3. Check available disk space
4. Close any applications that might be using the files

### During Organization
1. Don't modify the source or destination folders while the process is running
2. Keep the application window open
3. Monitor the progress bar for status updates

### After Organization
1. Verify the new folder structure
2. Check that all files are in their correct locations
3. Test a few files to ensure they play correctly

## Advanced Features

### Custom Settings
The application saves your settings between sessions:
- Selected folders
- Sound preferences
- Window position and size

### Performance
- The application processes files in batches for better performance
- Progress tracking shows estimated time remaining
- Memory usage is optimized for large music collections

### Security
- File integrity is verified during organization
- Secure file deletion is available for temporary files
- Path validation prevents security issues

## Support
If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review the documentation
3. Open an issue on the GitHub repository
4. Contact the maintainers

## Updates
The application will notify you when updates are available. To update:
1. Download the latest release
2. Install the new version
3. Your settings will be preserved

## Contributing
If you'd like to contribute to the project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License
This project is licensed under the MIT License. See the LICENSE file for details. 