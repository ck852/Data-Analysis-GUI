"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

# data_analysis_gui/dialogs/current_density_results_window.py
"""
Window for displaying and interacting with current density analysis results.

This module provides a window that allows for dynamic recalculation of current
density by editing Cslow values directly in the results table. It includes
features like live plot updates, input validation, and enhanced user experience
for streamlined data analysis.

Author: Data Analysis GUI Contributors
License: MIT
"""

import os
import re
from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Dict

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QSplitter, QVBoxLayout,
                             QWidget)

from data_analysis_gui.config.logging import get_logger
from data_analysis_gui.config.themes import (style_button, style_label,
                                             style_main_window, style_splitter)
from data_analysis_gui.core.models import BatchAnalysisResult
from data_analysis_gui.gui_services import FileDialogService
from data_analysis_gui.services.current_density_service import CurrentDensityService
from data_analysis_gui.widgets.shared_widgets import (BatchFileListWidget,
                                                      DynamicBatchPlotWidget,
                                                      FileSelectionState)

from data_analysis_gui.core.plot_formatter import PlotFormatter

logger = get_logger(__name__)


class CurrentDensityResultsWindow(QMainWindow):
    """Window for displaying current density results with interactive features."""

    def __init__(self, parent, batch_result: BatchAnalysisResult,
                 cslow_mapping: Dict[str, float], data_service,
                 batch_service=None):
        super().__init__(parent)

        self.original_batch_result = batch_result
        self.active_batch_result = deepcopy(batch_result)

        selected = getattr(batch_result, 'selected_files',
                           {r.base_name for r in batch_result.successful_results})
        self.selection_state = FileSelectionState(selected)

        self.plot_formatter = PlotFormatter()

        self.cslow_mapping = cslow_mapping
        self.data_service = data_service
        self.batch_service = batch_service
        self.file_dialog_service = FileDialogService()
        self.cd_service = CurrentDensityService()

        self.y_unit = "pA/pF"

        num_files = len(self.active_batch_result.successful_results)
        self.setWindowTitle(f"Current Density Results ({num_files} files)")

        # Set window size and position
        screen = self.screen() or QApplication.primaryScreen()
        avail = screen.availableGeometry()
        self.resize(int(avail.width() * 0.9), int(avail.height() * 0.9))
        self.move(avail.center() - self.rect().center())

        self.init_ui()

        # Apply centralized styling from themes.py
        style_main_window(self)

    def init_ui(self):
        """Initialize the UI with file list, plot, and controls."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)

        info_label = QLabel("(Click Cslow values to edit)")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        style_label(info_label, "caption") # Use themed label style
        main_layout.addWidget(info_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        style_splitter(splitter) # Use themed splitter style
        splitter.addWidget(self._create_left_panel())

        self.plot_widget = DynamicBatchPlotWidget()
        plot_labels = self.plot_formatter.get_plot_titles_and_labels('current_density')
        self.plot_widget.initialize_plot(
            x_label=plot_labels['x_label'],
            y_label=plot_labels['y_label'],
            title=plot_labels['title']
        )
        splitter.addWidget(self.plot_widget)

        splitter.setSizes([450, 850])
        main_layout.addWidget(splitter)

        self._add_export_controls(main_layout)

        self._apply_initial_current_density()
        self._populate_file_list()
        self._update_plot()

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with file list and controls."""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        self.file_list = BatchFileListWidget(self.selection_state, show_cslow=True)
        self.file_list.selection_changed.connect(self._update_plot)
        self.file_list.cslow_value_changed.connect(self._on_cslow_changed)
        layout.addWidget(self.file_list)

        controls_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_none_btn = QPushButton("Select None")
        style_button(select_all_btn, "secondary") # Use themed button style
        style_button(select_none_btn, "secondary") # Use themed button style
        select_all_btn.clicked.connect(lambda: self.file_list.set_all_checked(True))
        select_none_btn.clicked.connect(lambda: self.file_list.set_all_checked(False))
        controls_layout.addWidget(select_all_btn)
        controls_layout.addWidget(select_none_btn)
        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        self.summary_label = QLabel()
        layout.addWidget(self.summary_label)

        return panel

    def _add_export_controls(self, layout):
        """Add export buttons to the bottom of the window."""
        button_layout = QHBoxLayout()

        export_individual_btn = QPushButton("Export Individual CSVs...")
        style_button(export_individual_btn, "secondary")

        export_summary_btn = QPushButton("Export Summary CSV...")
        style_button(export_summary_btn, "primary")

        export_plot_btn = QPushButton("Export Plot...")
        style_button(export_plot_btn, "secondary")

        export_individual_btn.clicked.connect(self._export_individual_csvs)
        export_summary_btn.clicked.connect(self._export_summary)
        export_plot_btn.clicked.connect(self._export_plot)

        button_layout.addStretch()
        button_layout.addWidget(export_individual_btn)
        button_layout.addWidget(export_summary_btn)
        button_layout.addWidget(export_plot_btn)
        layout.addLayout(button_layout)

    def _sort_results(self, results):
        """Sort results numerically based on filename."""
        def extract_number(file_name):
            match = re.search(r'_(\d+)', file_name)
            return int(match.group(1)) if match else 0
        return sorted(results, key=lambda r: extract_number(r.base_name))

    def _populate_file_list(self):
        """Fill the file list with data from the batch result."""
        sorted_results = self._sort_results(self.active_batch_result.successful_results)
        color_mapping = self.plot_widget._generate_color_mapping(sorted_results)

        self.file_list.setRowCount(0)
        for result in sorted_results:
            color = color_mapping[result.base_name]
            cslow = self.cslow_mapping.get(result.base_name, 0.0)
            self.file_list.add_file(result.base_name, color, cslow)

        self._update_summary()

    def _on_cslow_changed(self, file_name: str, new_cslow: float):
        """Handle live recalculation when a Cslow value is changed."""
        try:
            self._recalculate_cd_for_file(file_name, new_cslow)
            result = next((r for r in self.active_batch_result.successful_results
                           if r.base_name == file_name), None)
            if result:
                self.plot_widget.update_line_data(
                    file_name,
                    result.y_data,
                    result.y_data2 if self.active_batch_result.parameters.use_dual_range else None
                )
                self.plot_widget.auto_scale_to_data()
        except (ValueError, ZeroDivisionError) as e:
            logger.warning(f"Invalid Cslow value for {file_name}: {e}")

    def _recalculate_cd_for_file(self, file_name: str, new_cslow: float):
        """Recalculate current density for a single file by creating a new result object."""
        results_list = self.active_batch_result.successful_results
        original_result = next(
            (r for r in self.original_batch_result.successful_results if r.base_name == file_name), None)

        try:
            target_index = next(
                (i for i, r in enumerate(results_list) if r.base_name == file_name))
        except StopIteration:
            logger.error(f"Could not find result for {file_name} in active list.")
            return

        if original_result is None:
            logger.error(f"Could not find original result for {file_name}.")
            return

        new_y_data = np.array(original_result.y_data) / new_cslow
        
        # Update export_table with new current density values
        new_export_table = None
        if original_result.export_table:
            new_export_table = deepcopy(original_result.export_table)
            if 'data' in new_export_table:
                # Update y_data column(s) in export table
                data_array = np.array(new_export_table['data'])
                if len(data_array.shape) == 2 and data_array.shape[1] >= 2:
                    # Column 1 is typically y_data (column 0 is x_data)
                    data_array[:, 1] = new_y_data
                    new_export_table['data'] = data_array
            
            # Update headers to reflect current density units
            self._update_export_table_headers(new_export_table, is_current_density=True)
        
        updated_result = replace(results_list[target_index], 
                                y_data=new_y_data,
                                export_table=new_export_table)

        if self.active_batch_result.parameters.use_dual_range and original_result.y_data2 is not None:
            new_y_data2 = np.array(original_result.y_data2) / new_cslow
            
            # Update second y_data column in export table for dual range
            if new_export_table and 'data' in new_export_table:
                data_array = np.array(new_export_table['data'])
                if data_array.shape[1] >= 3:
                    # Column 2 is y_data2 for dual range
                    data_array[:, 2] = new_y_data2
                    new_export_table['data'] = data_array
            
            updated_result = replace(updated_result, y_data2=new_y_data2, export_table=new_export_table)

        results_list[target_index] = updated_result
        self.cslow_mapping[file_name] = new_cslow

    def _update_plot(self):
        """Update the plot based on the current selections and data."""
        sorted_results = self._sort_results(self.active_batch_result.successful_results)
        self.plot_widget.set_data(
            sorted_results,
            use_dual_range=self.active_batch_result.parameters.use_dual_range
        )
        self.plot_widget.update_visibility(self.selection_state.get_selected_files())
        self.plot_widget.auto_scale_to_data()
        self._update_summary()

    def _update_summary(self):
        """Update the summary label text."""
        selected = len(self.selection_state.get_selected_files())
        total = len(self.active_batch_result.successful_results)
        self.summary_label.setText(f"{selected} of {total} files selected")

    def _validate_all_cslow_values(self) -> bool:
        """Validate Cslow values for all selected files before exporting."""
        for row in range(self.file_list.rowCount()):
            cslow_widget = self.file_list.cellWidget(row, 3)
            if cslow_widget and hasattr(cslow_widget, 'text'):
                try:
                    if float(cslow_widget.text()) <= 0: return False
                except ValueError:
                    return False
        return True

    def _apply_initial_current_density(self):
        """Apply initial current density calculations to all files."""
        original_results = {r.base_name: r for r in self.original_batch_result.successful_results}
        for i, result in enumerate(self.active_batch_result.successful_results):
            file_name = result.base_name
            cslow = self.cslow_mapping.get(file_name, 0.0)
            if cslow > 0 and file_name in original_results:
                original_result = original_results[file_name]
                new_y_data = np.array(original_result.y_data) / cslow
                
                # Update export_table with current density values
                new_export_table = None
                if original_result.export_table:
                    new_export_table = deepcopy(original_result.export_table)
                    if 'data' in new_export_table:
                        data_array = np.array(new_export_table['data'])
                        if len(data_array.shape) == 2 and data_array.shape[1] >= 2:
                            data_array[:, 1] = new_y_data
                            new_export_table['data'] = data_array
                    
                    # Update headers to reflect current density units
                    self._update_export_table_headers(new_export_table, is_current_density=True)
                
                updated_result = replace(result, y_data=new_y_data, export_table=new_export_table)
                
                if self.active_batch_result.parameters.use_dual_range and original_result.y_data2 is not None:
                    new_y_data2 = np.array(original_result.y_data2) / cslow
                    
                    # Update second y_data column in export table for dual range
                    if new_export_table and 'data' in new_export_table:
                        data_array = np.array(new_export_table['data'])
                        if data_array.shape[1] >= 3:
                            data_array[:, 2] = new_y_data2
                            new_export_table['data'] = data_array
                    
                    updated_result = replace(updated_result, y_data2=new_y_data2, export_table=new_export_table)
                
                self.active_batch_result.successful_results[i] = updated_result
        logger.debug(f"Applied initial current density calculations.")

    def _export_individual_csvs(self):
        """Export individual CSVs for selected files with current density values."""
        selected_files = self.selection_state.get_selected_files()
        if not selected_files:
            QMessageBox.warning(self, "No Data", "No files selected for export.")
            return

        if not self._validate_all_cslow_values():
            QMessageBox.warning(self, "Invalid Input", "Please correct invalid Cslow values before exporting.")
            return

        output_dir = self.file_dialog_service.get_directory(self, "Select Output Directory")
        if not output_dir:
            return

        try:
            filtered_results = [r for r in self.active_batch_result.successful_results if r.base_name in selected_files]
            if not filtered_results:
                QMessageBox.warning(self, "No Data", "No valid results to export.")
                return

            # Add "_CD" suffix to filenames for current density exports
            cd_results = []
            for result in filtered_results:
                cd_result = replace(result, base_name=f"{result.base_name}_CD")
                cd_results.append(cd_result)

            filtered_batch = replace(
                self.active_batch_result,
                successful_results=cd_results,
                failed_results=[],
                selected_files=selected_files
            )
            
            export_result = self.batch_service.export_results(filtered_batch, output_dir)
            success_count = sum(1 for r in export_result.export_results if r.success)

            if success_count > 0:
                QMessageBox.information(self, "Export Complete", f"Exported {success_count} current density files")
            else:
                QMessageBox.warning(self, "Export Failed", "No files were exported successfully.")
        except Exception as e:
            logger.error(f"CSV export failed: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed", f"Export failed: {str(e)}")

    def _update_export_table_headers(self, export_table, is_current_density=True):
        """
        Update export table headers to reflect current density units.
        
        Args:
            export_table: The export table dictionary to update
            is_current_density: If True, update to current density units (pA/pF)
        """
        if not export_table or 'headers' not in export_table:
            return
        
        # Get current units from parameters
        current_units = 'pA'  # default
        if hasattr(self.original_batch_result.parameters, 'channel_config'):
            config = self.original_batch_result.parameters.channel_config
            if config:
                current_units = config.get('current_units', 'pA')
        
        # Determine the unit to use
        if is_current_density:
            unit = f"{current_units}/pF"
        else:
            unit = current_units
        
        # Update headers that contain current measurements
        updated_headers = []
        for header in export_table['headers']:
            if 'Current' in header and '(' in header and ')' in header:
                # Replace the unit in parentheses
                base_label = header.split('(')[0].strip()
                updated_headers.append(f"{base_label} ({unit})")
            else:
                updated_headers.append(header)
        
        export_table['headers'] = updated_headers

    def _export_summary(self):
        """Export current density summary after validating inputs."""
        if not self._validate_all_cslow_values():
            QMessageBox.warning(self, "Invalid Input", "Please correct invalid Cslow values before exporting.")
            return

        file_path = self.file_dialog_service.get_export_path(self, "Current_Density_Summary.csv")
        if not file_path:
            return

        try:
            selected_files = self.selection_state.get_selected_files()
            sorted_results = [r for r in self._sort_results(self.active_batch_result.successful_results)
                              if r.base_name in selected_files]
            voltage_data, file_mapping = {}, {}

            for idx, result in enumerate(sorted_results):
                recording_id = f"Recording {idx + 1}"
                file_mapping[recording_id] = result.base_name
                for i, voltage in enumerate(result.x_data):
                    voltage_rounded = round(float(voltage), 1)
                    if voltage_rounded not in voltage_data:
                        voltage_data[voltage_rounded] = [np.nan] * len(sorted_results)
                    if i < len(result.y_data):
                        voltage_data[voltage_rounded][idx] = result.y_data[i]

            export_data = self.cd_service.prepare_summary_export(
                voltage_data, file_mapping, self.cslow_mapping, selected_files, self.y_unit
            )
            result = self.data_service.export_to_csv(export_data, file_path)

            if result.success:
                QMessageBox.information(self, "Export Complete", f"Exported summary for {len(selected_files)} files.")
            else:
                QMessageBox.warning(self, "Export Failed", result.error_message)
        except Exception as e:
            logger.error(f"Failed to export summary: {e}", exc_info=True)
            QMessageBox.critical(self, "Export Failed", f"Export failed: {str(e)}")

    def _export_plot(self):
        """Export the current plot to an image file."""
        file_path = self.file_dialog_service.get_export_path(
            self, "current_density_plot.png",
            file_types="PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")

        if file_path:
            try:
                self.plot_widget.export_figure(file_path)
                QMessageBox.information(self, "Export Complete", f"Plot saved to {Path(file_path).name}")
            except Exception as e:
                logger.error(f"Failed to export plot: {e}", exc_info=True)
                QMessageBox.critical(self, "Export Failed", str(e))