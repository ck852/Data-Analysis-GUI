# batch_results_window.py

from pathlib import Path
import re
from typing import Set
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
                             QCheckBox, QLabel, QSplitter, QHeaderView, QApplication,
                             QGroupBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPixmap, QPainter, QBrush

from data_analysis_gui.gui_services import FileDialogService
from data_analysis_gui.core.plot_formatter import PlotFormatter
from data_analysis_gui.config.logging import get_logger

from data_analysis_gui.dialogs.current_density_dialog import CurrentDensityDialog
from data_analysis_gui.dialogs.current_density_results_window import CurrentDensityResultsWindow

from data_analysis_gui.widgets.shared_widgets import (
    DynamicBatchPlotWidget, BatchFileListWidget, FileSelectionState
)

from data_analysis_gui.config.themes import (
    style_main_window, create_styled_button, style_group_box, 
    get_selection_summary_color, style_label, style_splitter
)

logger = get_logger(__name__)


class BatchResultsWindow(QMainWindow):
    """Window for displaying batch analysis results with file selection."""
    
    def __init__(self, parent, batch_result, batch_service, plot_service, data_service):
        super().__init__(parent)
        
        # Initialize selection state if not present
        if batch_result.selected_files is None:
            from dataclasses import replace
            batch_result = replace(
                batch_result,
                selected_files={r.base_name for r in batch_result.successful_results}
            )
        
        self.batch_result = batch_result
        self.batch_service = batch_service
        self.plot_service = plot_service
        self.data_service = data_service
        self.file_dialog_service = FileDialogService()
        
        # Create selection state object
        self.selection_state = FileSelectionState(self.batch_result.selected_files)
        
        # Use PlotFormatter for consistent formatting
        self.plot_formatter = PlotFormatter()
        
        self.setWindowTitle("Batch Analysis Results")
        screen = self.screen() or QApplication.primaryScreen()
        avail = screen.availableGeometry()
        self.resize(int(avail.width() * 0.9), int(avail.height() * 0.9))
        fg = self.frameGeometry()
        fg.moveCenter(avail.center())
        self.move(fg.topLeft())
        self.init_ui()
        
        # Apply theme from themes.py
        style_main_window(self)
    
    def init_ui(self):
        """Initialize the UI."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Create splitter for file list and plot
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: File list with controls
        left_panel = self._create_file_list_panel()
        splitter.addWidget(left_panel)
        
        # Right panel: Plot
        self.plot_widget = DynamicBatchPlotWidget()
        plot_labels = self.plot_formatter.get_plot_titles_and_labels(
            'batch', params=self.batch_result.parameters
        )
        self.plot_widget.initialize_plot(
            x_label=plot_labels['x_label'],
            y_label=plot_labels['y_label'],
            title=plot_labels['title']
        )
        splitter.addWidget(self.plot_widget)
        
        # Set initial splitter sizes (30% list, 70% plot)
        splitter.setSizes([360, 840])
        
        main_layout.addWidget(splitter)
        
        # Export controls at bottom
        self._add_export_controls(main_layout)
        
        # Populate and initial plot
        self._populate_file_list()
        self._update_plot()
    
    def _create_file_list_panel(self) -> QWidget:
        """Create the file list panel."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Title
        title = QLabel("Files:")
        style_label(title, 'subheading')
        layout.addWidget(title)
        
        # File list widget - use the shared widget
        self.file_list = BatchFileListWidget(self.selection_state, show_cslow=False)
        self.file_list.selection_changed.connect(self._on_selection_changed)
        layout.addWidget(self.file_list)
        
        # Selection controls
        controls_layout = QHBoxLayout()
        select_all_btn = create_styled_button("Select All", "secondary", panel)
        select_none_btn = create_styled_button("Select None", "secondary", panel)
        
        select_all_btn.clicked.connect(lambda: self.file_list.set_all_checked(True))
        select_none_btn.clicked.connect(lambda: self.file_list.set_all_checked(False))
        
        controls_layout.addWidget(select_all_btn)
        controls_layout.addWidget(select_none_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Summary label
        self.summary_label = QLabel()
        style_label(self.summary_label, 'caption')
        layout.addWidget(self.summary_label)
        
        return panel
    
    def _sort_results(self, results):
        """Sort results numerically by file name."""
        def extract_number(file_name):
            match = re.search(r'_(\d+)', file_name)
            if match:
                return int(match.group(1))
            numbers = re.findall(r'\d+', file_name)
            if numbers:
                return int(numbers[-1])
            return 0
        
        return sorted(results, key=lambda r: extract_number(r.base_name))
    
    def _populate_file_list(self):
        """Populate the file list with sorted results and colors."""
        sorted_results = self._sort_results(self.batch_result.successful_results)
        
        # Generate color mapping
        color_mapping = self.plot_widget._generate_color_mapping(sorted_results)
        
        # Clear and populate file list
        self.file_list.setRowCount(0)
        
        for result in sorted_results:
            color = color_mapping[result.base_name]
            self.file_list.add_file(result.base_name, color)
    
    def _update_plot(self):
        """Update the plot based on selected files."""
        sorted_results = self._sort_results(self.batch_result.successful_results)
        
        self.plot_widget.set_data(
            sorted_results,
            use_dual_range=self.batch_result.parameters.use_dual_range
        )
        
        self.plot_widget.update_visibility(self.selection_state.get_selected_files())
        self._update_summary()
    
    def _on_selection_changed(self):
        """Handle file selection changes."""
        self.plot_widget.update_visibility(self.selection_state.get_selected_files())
        self._update_summary()
    
    def _update_summary(self):
        """Update the summary label using theme utilities."""
        selected = len(self.selection_state.get_selected_files())
        total = len(self.batch_result.successful_results)
        
        color = get_selection_summary_color(selected, total)
        
        self.summary_label.setText(f"{selected} of {total} files selected")
        self.summary_label.setStyleSheet(f"color: {color}; font-weight: 500; font-style: normal;")
    
    def _add_export_controls(self, layout):
        """Add export controls."""
        export_group = QGroupBox("Export Options")
        style_group_box(export_group)
        
        button_layout = QHBoxLayout(export_group)
        
        # Create buttons
        export_csvs_btn = create_styled_button("Export Individual CSVs...", "secondary", self)
        export_plot_btn = create_styled_button("Export Plot...", "secondary", self)
        
        # IV-specific exports if applicable
        if self._is_iv_analysis():
            export_iv_summary_btn = create_styled_button("Export IV Summary...", "accent", self)
            button_layout.addWidget(export_iv_summary_btn)
            export_iv_summary_btn.clicked.connect(self._export_iv_summary)
            
            current_density_btn = create_styled_button("Current Density Analysis...", "primary", self)
            button_layout.addWidget(current_density_btn)
            current_density_btn.clicked.connect(self._open_current_density_analysis)
        
        button_layout.addWidget(export_csvs_btn)
        button_layout.addWidget(export_plot_btn)
        button_layout.addStretch()
        
        layout.addWidget(export_group)
        
        # Connect signals
        export_csvs_btn.clicked.connect(self._export_individual_csvs)
        export_plot_btn.clicked.connect(self._export_plot)
    
    def _is_iv_analysis(self):
        """Check if this is an IV analysis."""
        params = self.batch_result.parameters
        return (
            params.x_axis.channel == "Voltage"
            and params.y_axis.channel == "Current"
            and {params.x_axis.measure, params.y_axis.measure} <= {"Average", "Current"}
        )
    
    def _get_filtered_results(self):
        """Get results filtered by current selection."""
        selected_files = self.selection_state.get_selected_files()
        filtered = [
            r for r in self.batch_result.successful_results
            if r.base_name in selected_files
        ]
        return self._sort_results(filtered)
    
    def _export_iv_summary(self):
        """Export IV summary for selected files only."""
        from data_analysis_gui.core.iv_analysis import IVAnalysisService, IVSummaryExporter
        
        filtered_results = self._get_filtered_results()
        
        if not filtered_results:
            QMessageBox.warning(self, "No Data", "No files selected for export.")
            return
        
        batch_data = {
            r.base_name: {
                'x_values': r.x_data.tolist(),
                'y_values': r.y_data.tolist(),
                'x_values2': r.x_data2.tolist() if r.x_data2 is not None else None,
                'y_values2': r.y_data2.tolist() if r.y_data2 is not None else None
            }
            for r in filtered_results
        }
        
        iv_data_r1, mapping, iv_data_r2 = IVAnalysisService.prepare_iv_data(
            batch_data, self.batch_result.parameters
        )
        
        file_path = self.file_dialog_service.get_export_path(
            self, "IV_Summary.csv",
            file_types="CSV files (*.csv)"
        )
        
        if file_path:
            try:
                selected_set = set(r.base_name for r in filtered_results)
                table = IVSummaryExporter.prepare_summary_table(
                    iv_data_r1, mapping, selected_set
                )
                
                result = self.data_service.export_to_csv(table, file_path)
                
                if result.success:
                    QMessageBox.information(
                        self, "Export Complete",
                        f"Exported IV summary with {len(filtered_results)} files"
                    )
                else:
                    QMessageBox.warning(self, "Export Failed", result.error_message)
                    
            except Exception as e:
                logger.error(f"IV summary export failed: {e}", exc_info=True)
                QMessageBox.critical(self, "Export Failed", str(e))
    
    def _export_individual_csvs(self):
        """Export individual CSVs for selected files only."""
        filtered_results = self._get_filtered_results()
        
        if not filtered_results:
            QMessageBox.warning(self, "No Data", "No files selected for export.")
            return
        
        output_dir = self.file_dialog_service.get_directory(
            self, "Select Output Directory"
        )
        
        if output_dir:
            try:
                from data_analysis_gui.core.models import BatchAnalysisResult
                from dataclasses import replace
                
                filtered_batch = replace(
                    self.batch_result,
                    successful_results=filtered_results,
                    failed_results=[],
                    selected_files=self.selection_state.get_selected_files()
                )
                
                result = self.batch_service.export_results(filtered_batch, output_dir)
                
                success_count = sum(1 for r in result.export_results if r.success)
                
                QMessageBox.information(
                    self, "Export Complete",
                    f"Exported {success_count} files\nTotal: {result.total_records} records"
                )
                
            except Exception as e:
                logger.error(f"Export failed: {e}", exc_info=True)
                QMessageBox.critical(self, "Export Failed", str(e))
    
    def _export_plot(self):
        """Export current plot (with selected files only)."""
        if not self.plot_widget.figure:
            QMessageBox.warning(self, "No Plot", "No plot to export.")
            return
        
        file_path = self.file_dialog_service.get_export_path(
            self, "batch_plot.png",
            file_types="PNG files (*.png);;PDF files (*.pdf);;SVG files (*.svg)"
        )
        
        if file_path:
            try:
                self.plot_widget.export_figure(file_path)
                QMessageBox.information(
                    self, "Export Complete",
                    f"Plot saved to {Path(file_path).name}"
                )
            except Exception as e:
                logger.error(f"Failed to export plot: {e}")
                QMessageBox.critical(self, "Export Failed", str(e))
    
    def _open_current_density_analysis(self):
        """Open current density analysis dialog."""
        from dataclasses import replace
        batch_with_selection = replace(
            self.batch_result,
            selected_files=self.selection_state.get_selected_files()
        )
        
        dialog = CurrentDensityDialog(self, batch_with_selection)
        
        if dialog.exec_():
            cslow_mapping = dialog.get_cslow_mapping()
            
            if not cslow_mapping:
                QMessageBox.warning(
                    self, 
                    "No Data", 
                    "No Cslow values were entered."
                )
                return
            
            cd_window = CurrentDensityResultsWindow(
                self,
                batch_with_selection,
                cslow_mapping,
                self.data_service,
                self.batch_service
            )
            cd_window.show()