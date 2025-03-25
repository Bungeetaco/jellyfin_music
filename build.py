"""
Build script for creating the Jellyfin Music Organizer executable.
"""

import os
import shutil
from typing import List, Tuple, Optional
from pathlib import Path
import sys
import logging

import PyInstaller.__main__

# Define resource paths
ICON_PATH = os.path.join("jellyfin_music_organizer", "resources", "Octopus.ico")
NOTIFICATION_AUDIO_DIR = "notification_audio"
BUILD_DIR = "dist"

logger = logging.getLogger(__name__)


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


def create_spec_file(
    entry_point: str, name: str, icon_path: str, additional_data: List[Tuple[str, str]]
) -> None:
    """
    Create a PyInstaller spec file.

    Args:
        entry_point: Path to the main script
        name: Name of the output executable
        icon_path: Path to the icon file
        additional_data: List of (source, dest) tuples for additional files
    """
    try:
        # Validate inputs
        if not all([entry_point, name, icon_path]):
            raise ValueError("Missing required parameters")

        # Create spec file content
        spec_content = (
            f"# -*- mode: python ; coding: utf-8 -*-\n\n"
            f"block_cipher = None\n\n"
            f"a = Analysis(['{entry_point}'],\n"
            f"    pathex=[],\n"
            f"    binaries=[],\n"
            f"    datas={additional_data},\n"
            f"    hiddenimports=[],\n"
            f"    hookspath=[],\n"
            f"    runtime_hooks=[],\n"
            f"    excludes=[],\n"
            f"    win_no_prefer_redirects=False,\n"
            f"    win_private_assemblies=False,\n"
            f"    cipher=block_cipher,\n"
            f"    noarchive=False)\n"
        )

        # Write spec file
        spec_path = Path(f"{name}.spec")
        spec_path.write_text(spec_content, encoding='utf-8')
        logger.info(f"Created spec file: {spec_path}")

    except Exception as e:
        logger.error(f"Failed to create spec file: {e}")
        raise


if __name__ == "__main__":
    print("Building executable...")
    build_executable()
    print("Copying additional files...")
    copy_additional_files()
    print("Build complete! Executable is in the 'dist' directory.")
