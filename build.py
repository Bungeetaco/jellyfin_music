"""
Build script for creating the Jellyfin Music Organizer executable.
"""

import os
import shutil
import sys

import PyInstaller.__main__

# Define resource paths
ICON_PATH = os.path.join("jellyfin_music_organizer", "resources", "Octopus.ico")
NOTIFICATION_AUDIO_DIR = "notification_audio"
BUILD_DIR = "dist"


def ensure_resources_exist():
    """Ensure all required resource files exist."""
    required_files = [
        (ICON_PATH, "Application icon"),
        (os.path.join(NOTIFICATION_AUDIO_DIR, "audio_ding.wav"), "Notification sound"),
        (os.path.join(NOTIFICATION_AUDIO_DIR, "audio_complete.wav"), "Completion sound"),
    ]

    missing_files = []
    for file_path, description in required_files:
        if not os.path.exists(file_path):
            missing_files.append(f"- {description}: {file_path}")

    if missing_files:
        print("Error: Required resource files are missing:")
        print("\n".join(missing_files))
        return False

    return True


def get_pyinstaller_args():
    """Get PyInstaller arguments with optional file handling."""
    args = [
        "main.py",  # Main script
        "--name=JellyfinMusicOrganizer",  # Name of the executable
        "--windowed",  # Use GUI mode
        "--onefile",  # Create a single executable
        f"--icon={ICON_PATH}",  # Application icon
        f"--add-data={NOTIFICATION_AUDIO_DIR};{NOTIFICATION_AUDIO_DIR}",  # Include notification sounds
        "--add-data=jellyfin_music_organizer;jellyfin_music_organizer",  # Include the entire module
        "--clean",  # Clean PyInstaller cache
        "--noconfirm",  # Replace existing build without asking
        "--hidden-import=PyQt5",
        "--hidden-import=mutagen",
        "--hidden-import=qdarkstyle",
        "--hidden-import=jellyfin_music_organizer",
        "--hidden-import=jellyfin_music_organizer.core",
        "--hidden-import=jellyfin_music_organizer.ui",
        "--hidden-import=jellyfin_music_organizer.utils",
    ]

    # Add optional files if they exist
    optional_files = ["config.json", "README.md", "LICENSE"]
    for file in optional_files:
        if os.path.exists(file):
            args.append(f"--add-data={file};.")
        else:
            print(f"Note: Optional file '{file}' not found, skipping...")

    return args


def build_executable():
    """Build the executable using PyInstaller."""
    # Check if resources exist
    if not ensure_resources_exist():
        return

    # Get PyInstaller arguments
    args = get_pyinstaller_args()

    # Run PyInstaller
    print("Starting PyInstaller build...")
    PyInstaller.__main__.run(args)


def copy_additional_files():
    """Copy additional files to the build directory."""
    # Create necessary directories
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Copy documentation if it exists
    if os.path.exists("docs"):
        shutil.copytree("docs", os.path.join(BUILD_DIR, "docs"), dirs_exist_ok=True)
        print("Documentation copied successfully")


if __name__ == "__main__":
    print("Building executable...")
    build_executable()
    print("Copying additional files...")
    copy_additional_files()
    print("Build complete! Executable is in the 'dist' directory.")
