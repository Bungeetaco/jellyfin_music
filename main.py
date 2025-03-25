from PyQt5.QtWidgets import QApplication
import qdarkstyle

# Import the main window class
from jellyfin_music_organizer.main import MusicOrganizer

# Create and run application
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = MusicOrganizer()
    window.show()  # Make sure to show the window
    app.exec_()
    