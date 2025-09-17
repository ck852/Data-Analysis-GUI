import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from data_analysis_gui.main_window import MainWindow

# Import from refactored themes module
from data_analysis_gui.config.themes import apply_theme_to_application

def main():
    # Enable high DPI scaling BEFORE creating QApplication
   # if hasattr(Qt, 'AA_EnableHighDpiScaling'):
       # QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    # if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    #     QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # Apply modern theme globally (handles style, palette, and base stylesheet)
    apply_theme_to_application(app)

    # Set application properties
    app.setApplicationName("Electrophysiology File Sweep Analyzer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CKS")

    # Set a reasonable default font size
    font = app.font()
    if font.pointSize() < 7:  # If system font is too small
        font.setPointSize(7)  # Set to readable size
        app.setFont(font)

    # No need to set style again - apply_theme_to_application handles it

    # Create main window
    window = MainWindow()

    # Ensure we are not starting maximized
    window.setWindowState(Qt.WindowState.WindowNoState)

    # Constrain window size to a fraction of the available screen
    screen = app.primaryScreen()
    avail = screen.availableGeometry() if screen else None

    screen = app.primaryScreen().availableGeometry()
    scale = 0.9   # use 0.9 for 90%
    w, h = int(screen.width() * scale), int(screen.height() * scale)
    window.resize(w, h)

    # center
    frame = window.frameGeometry()
    frame.moveCenter(screen.center())
    window.move(frame.topLeft())

    window.show()
    sys.exit(app.exec())

def run():
    """Entry point for the application."""
    main()

if __name__ == '__main__':
    main()