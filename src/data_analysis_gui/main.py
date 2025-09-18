"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

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
    
    # Apply modern theme globally
    apply_theme_to_application(app)
    
    # Set application properties
    app.setApplicationName("Electrophysiology File Sweep Analyzer")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("CKS")
    
    # Set a reasonable default font size
    font = app.font()
    if font.pointSize() < 7:
        font.setPointSize(7)
        app.setFont(font)
    
    # Create main window
    window = MainWindow()
    
    # Ensure we are not starting maximized
    window.setWindowState(Qt.WindowState.WindowNoState)
    
    # Calculate appropriate window size
    screen = app.primaryScreen()
    if screen:
        avail = screen.availableGeometry()
        
        # Get the window's size hints to respect minimum sizes
        min_size = window.minimumSizeHint()
        if not min_size.isValid():
            min_size = window.sizeHint()
        
        # Use 85% of available space, but respect minimums
        target_w = int(avail.width() * 0.85)
        target_h = int(avail.height() * 0.85)
        
        # Ensure we don't go below minimum sizes
        if min_size.isValid():
            target_w = max(target_w, min_size.width())
            target_h = max(target_h, min_size.height())
        
        # Also ensure we don't exceed available space
        max_w = avail.width() - 50
        max_h = avail.height() - 100
        
        final_w = min(target_w, max_w)
        final_h = min(target_h, max_h)
        
        # Set size and center
        window.resize(final_w, final_h)
        
        frame = window.frameGeometry()
        frame.moveCenter(avail.center())
        window.move(frame.topLeft())
    else:
        # Fallback size
        window.resize(1200, 800)
    
    window.show()
    
    # Process events to ensure geometry is applied
    app.processEvents()
    
    sys.exit(app.exec())

def run():
    """Entry point for the application."""
    main()

if __name__ == '__main__':
    main()