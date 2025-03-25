from setuptools import find_packages, setup

setup(
    name="jellyfin_music_organizer",
    version="3.06",
    packages=find_packages(),
    install_requires=[
        "PyQt5>=5.15.0",
        "qdarkstyle>=3.1",
        "mutagen>=1.45.0",
        "pathlib>=1.0.1",
        "openpyxl>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "jellyfin-music-organizer=jellyfin_music_organizer.main:main",
        ],
    },
    author="Gabriel",
    description="A tool for organizing music files based on their metadata",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.7",
)
