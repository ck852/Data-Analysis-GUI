# src/data_analysis_gui/dialogs/analysis_plot_dialog.py
"""
GUI dialog for displaying analysis plots.
Phase 3: Updated to use stateless AnalysisPlotter methods.
FIXED: Window positioning bug and full theme integration.
Updated for refactored themes.py
"""

import os
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                              QFileDialog, QMessageBox)
from pathlib import Path

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# Core imports - all data processing is delegated to these
from data_analysis_gui.core.analysis_plot import AnalysisPlotter, AnalysisPlotData
from data_analysis_gui.core.plot_formatter import PlotFormatter  # Import the formatter
from data_analysis_gui.gui_services import FileDialogService

# Updated theme imports for refactored version
from data_analysis_gui.config.themes import apply_modern_theme, style_button, create_styled_button


class AnalysisPlotDialog(QDialog):
    """
    Dialog for displaying analysis plot in a separate window.
    """
    
    def __init__(self, parent, plot_data, params, file_path, controller_or_manager=None):
        super().__init__(parent)
        
        # Initialize the formatter
        self.plot_formatter = PlotFormatter()

        # Generate labels and title using the formatter
        file_name = Path(file_path).stem if file_path else None
        plot_labels = self.plot_formatter.get_plot_titles_and_labels(
            'analysis', params=params, file_name=file_name
        )
        self.x_label = plot_labels['x_label']
        self.y_label = plot_labels['y_label']
        self.plot_title = plot_labels['title']
        
        # Store controller/manager and params for export
        self.controller = controller_or_manager
        self.params = params
        self.dataset = None  # Store dataset if passed directly

        # Initialize GUI service for file operations
        self.file_dialog_service = FileDialogService()

        # Convert plot data to AnalysisPlotData if needed
        if isinstance(plot_data, dict):
            self.plot_data_obj = AnalysisPlotData.from_dict(plot_data)
        else:
            self.plot_data_obj = plot_data
        
        self.setWindowTitle("Analysis Plot")
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(200, 200, int(screen.width() * 0.6), int(screen.height() * 0.7))
        self.init_ui()

        # Apply modern theme (refactored version uses single function)
        apply_modern_theme(self)
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        self.figure, self.ax = AnalysisPlotter.create_figure(
            self.plot_data_obj,
            self.x_label, 
            self.y_label,
            self.plot_title,
            figsize=(8, 6)
        )
        self.canvas = FigureCanvas(self.figure)
        
        # Create toolbar
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        
        self.figure.tight_layout()
        self.canvas.draw()
        
        # Add export buttons using the proper method
        self._add_export_controls(layout)
    
    def _add_export_controls(self, parent_layout):
        """Add export control buttons with full theme integration."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        
        # Export data button - primary action
        self.export_data_btn = create_styled_button("Export Data", "primary", self)
        self.export_data_btn.clicked.connect(self.export_data)
        button_layout.addWidget(self.export_data_btn)
        
        # Export image button - secondary action
        self.export_img_btn = create_styled_button("Export Image", "secondary", self)
        self.export_img_btn.clicked.connect(self.export_plot_image)
        button_layout.addWidget(self.export_img_btn)
        
        # Close button - secondary action
        self.close_btn = create_styled_button("Close", "secondary", self)
        self.close_btn.clicked.connect(self.close)
        
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        parent_layout.addLayout(button_layout)
    
    def export_plot_image(self):
        """
        Export plot as image using stateless plotter.
        
        PHASE 3: Updated to use static save_figure method.
        """
        file_path = self.file_dialog_service.get_export_path(
            parent=self,
            suggested_name="analysis_plot.png",
            file_types="PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg);;All files (*.*)"
        )
        
        if file_path:
            try:
                # Use static method to save
                AnalysisPlotter.save_figure(self.figure, file_path, dpi=300)
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Plot saved to {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Failed",
                    f"Failed to save plot: {str(e)}"
                )
    
    def export_data(self):
        """
        Export plot data with proper separation of concerns.
        """
        if not self.controller or not self.params:
            QMessageBox.warning(
                self,
                "Export Error",
                "Export functionality requires controller context"
            )
            return
        
        # Determine what type of object we have
        if hasattr(self.controller, 'export_analysis_data'):
            # It's an ApplicationController
            suggested_filename = self.controller.get_suggested_export_filename(self.params)
        elif hasattr(self.controller, 'export_analysis'):
            # It's an AnalysisManager
            if hasattr(self.controller, 'data_manager'):
                suggested_filename = self.controller.data_manager.suggest_filename(
                    self.parent().current_file_path if hasattr(self.parent(), 'current_file_path') else "analysis",
                    "",
                    self.params
                )
            else:
                suggested_filename = "analysis_export.csv"
        else:
            suggested_filename = "analysis_export.csv"
        
        # Get path through GUI service
        file_path = self.file_dialog_service.get_export_path(
            parent=self,
            suggested_name=suggested_filename,
            file_types="CSV files (*.csv);;All files (*.*)"
        )
        
        if file_path:
            try:
                # Export based on what we have
                if hasattr(self.controller, 'export_analysis_data'):
                    # ApplicationController
                    result = self.controller.export_analysis_data(self.params, file_path)
                elif hasattr(self.controller, 'export_analysis') and self.dataset:
                    # AnalysisManager with dataset
                    result = self.controller.export_analysis(self.dataset, self.params, file_path)
                else:
                    QMessageBox.warning(self, "Export Error", "Export not available")
                    return
                
                # Show result
                if result.success:
                    QMessageBox.information(
                        self, 
                        "Export Successful", 
                        f"Exported {result.records_exported} records to {os.path.basename(file_path)}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Export Failed",
                        f"Export failed: {result.error_message}"
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Export Error",
                    f"Export failed: {str(e)}"
                )