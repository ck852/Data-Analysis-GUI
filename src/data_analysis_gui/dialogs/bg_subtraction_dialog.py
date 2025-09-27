"""
Background Subtraction Dialog for PatchBatch Electrophysiology Data Analysis Tool
Refactored to use centralized plot_style.py functions for consistency and maintainability.

Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

import numpy as np
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QMessageBox, QFormLayout
)
from PySide6.QtCore import Qt

from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from data_analysis_gui.config.themes import apply_modern_theme, create_styled_button
from data_analysis_gui.config.plot_style import (
    apply_plot_style, style_axis, get_line_styles, COLORS
)
from data_analysis_gui.widgets.custom_inputs import SelectAllSpinBox
from data_analysis_gui.core.dataset import ElectrophysiologyDataset
from data_analysis_gui.core.channel_definitions import ChannelDefinitions
from data_analysis_gui.core.data_extractor import DataExtractor
from data_analysis_gui.config.logging import get_logger

logger = get_logger(__name__)


class BackgroundSubtractionDialog(QDialog):
    """
    Dialog for defining background range and applying background subtraction.
    Refactored to use centralized plot_style.py functions for consistency.
    """
    
    def __init__(self, dataset: ElectrophysiologyDataset, sweep_index: str, 
                 channel_definitions: ChannelDefinitions, 
                 default_start: float = 0, default_end: float = 100,
                 parent=None):
        """
        Initialize the background subtraction dialog with centralized styling.
        
        Args:
            dataset: The electrophysiology dataset
            sweep_index: Current sweep index to display
            channel_definitions: Channel mapping definitions
            default_start: Default start time for background range (ms)
            default_end: Default end time for background range (ms)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.dataset = dataset
        self.sweep_index = sweep_index
        self.channel_definitions = channel_definitions
        self.data_extractor = DataExtractor(channel_definitions)
        
        self.setWindowTitle("Background Subtraction")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        # Apply global plot style for consistency
        apply_plot_style()
        
        # Get styling constants from plot_style.py
        self.colors = COLORS
        self.line_styles = get_line_styles()
        
        # Get current channel data for the plot
        self.time_ms, self.current_data = self._get_current_channel_data()
        
        if self.time_ms is None or self.current_data is None:
            QMessageBox.warning(self, "No Data", "No current channel data available.")
            self.reject()
            return
            
        # Validate and set default ranges
        max_time = self.time_ms[-1] if len(self.time_ms) > 0 else 1000
        self.default_start = max(0, min(default_start, max_time * 0.9))
        self.default_end = max(self.default_start + 10, min(default_end, max_time))
        
        self._init_ui()
        self._connect_signals()
        self._update_plot()
        
        # Apply modern theme
        apply_modern_theme(self)
        
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Create matplotlib plot
        self._create_plot()
        layout.addWidget(self.canvas)
        
        # Range controls
        range_widget = QWidget()
        range_layout = QFormLayout(range_widget)
        range_layout.setSpacing(8)
        
        self.start_spinbox = SelectAllSpinBox()
        self.start_spinbox.setDecimals(1)
        self.start_spinbox.setSuffix(" ms")
        self.start_spinbox.setMinimum(0)
        self.start_spinbox.setMaximum(self.time_ms[-1] if len(self.time_ms) > 0 else 10000)
        self.start_spinbox.setValue(self.default_start)
        self.start_spinbox.setMinimumWidth(120)
        
        self.end_spinbox = SelectAllSpinBox()
        self.end_spinbox.setDecimals(1)
        self.end_spinbox.setSuffix(" ms")
        self.end_spinbox.setMinimum(0)
        self.end_spinbox.setMaximum(self.time_ms[-1] if len(self.time_ms) > 0 else 10000)
        self.end_spinbox.setValue(self.default_end)
        self.end_spinbox.setMinimumWidth(120)
        
        range_layout.addRow("Background Start:", self.start_spinbox)
        range_layout.addRow("Background End:", self.end_spinbox)
        
        layout.addWidget(range_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = create_styled_button("Cancel", "secondary")
        self.apply_button = create_styled_button("Apply Background Subtraction", "primary")
        
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
        
    def _create_plot(self):
        """Create the matplotlib plot widget with centralized styling."""
        self.figure = Figure(figsize=(7, 3.5), facecolor=self.colors["light"])
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Basic axis setup will be handled by style_axis() in _update_plot()
        
    def _connect_signals(self):
        """Connect UI signals to their handlers."""
        self.start_spinbox.valueChanged.connect(self._update_plot)
        self.end_spinbox.valueChanged.connect(self._update_plot)
        self.apply_button.clicked.connect(self._apply_background_subtraction)
        self.cancel_button.clicked.connect(self.reject)
        
    def _get_current_channel_data(self):
        """
        Get current channel data for the specified sweep.
        
        Returns:
            Tuple[np.ndarray, np.ndarray]: Time and current data arrays, or (None, None) if failed
        """
        try:
            sweep_data = self.data_extractor.extract_sweep_data(self.dataset, self.sweep_index)
            return sweep_data["time_ms"], sweep_data["current"]
        except Exception as e:
            logger.error(f"Failed to extract current channel data: {e}")
            return None, None
            
    def _update_plot(self):
        """Update the plot using centralized styling functions."""
        if self.time_ms is None or self.current_data is None:
            return
            
        self.ax.clear()
        
        # Plot current data using primary color from style
        primary_style = self.line_styles["primary"]
        self.ax.plot(
            self.time_ms, 
            self.current_data, 
            color=primary_style["color"],
            linewidth=primary_style["linewidth"], 
            alpha=primary_style["alpha"]
        )
        
        # Add background range cursors using range1 styling
        start_time = self.start_spinbox.value()
        end_time = self.end_spinbox.value()
        
        range1_style = self.line_styles["range1"]
        self.ax.axvline(
            start_time, 
            color=range1_style["color"], 
            linestyle=range1_style["linestyle"],
            linewidth=range1_style["linewidth"], 
            alpha=range1_style["alpha"]
        )
        self.ax.axvline(
            end_time, 
            color=range1_style["color"], 
            linestyle=range1_style["linestyle"],
            linewidth=range1_style["linewidth"], 
            alpha=range1_style["alpha"]
        )
        
        # Highlight the background region with semi-transparent overlay
        if start_time < end_time:
            self.ax.axvspan(start_time, end_time, alpha=0.1, color=range1_style["color"])
        
        # Use centralized axis styling instead of manual formatting
        style_axis(
            self.ax,
            title=f"Current Trace - Sweep {self.sweep_index}",
            xlabel="Time (ms)",
            ylabel="Current (pA)",
            remove_top_right=True
        )
        
        # Add padding and refresh
        self.ax.relim()
        self.ax.autoscale_view(tight=True)
        self.ax.margins(x=0.02, y=0.05)
        
        self.figure.tight_layout(pad=1.0)
        self.canvas.draw_idle()
        
    def _validate_range(self):
        """
        Validate the background range.
        
        Returns:
            bool: True if range is valid, False otherwise
        """
        start_time = self.start_spinbox.value()
        end_time = self.end_spinbox.value()
        
        if start_time >= end_time:
            QMessageBox.warning(self, "Invalid Range", 
                              "Background start time must be less than end time.")
            return False
            
        if len(self.time_ms) > 0:
            if start_time < self.time_ms[0] or end_time > self.time_ms[-1]:
                QMessageBox.warning(self, "Invalid Range", 
                                  f"Background range must be within the sweep time bounds "
                                  f"({self.time_ms[0]:.1f} - {self.time_ms[-1]:.1f} ms).")
                return False
                
            # Check if range contains data points
            mask = (self.time_ms >= start_time) & (self.time_ms <= end_time)
            if not np.any(mask):
                QMessageBox.warning(self, "Invalid Range", 
                                  "Background range contains no data points.")
                return False
        
        return True
        
    def _apply_background_subtraction(self):
        """Apply background subtraction to the entire dataset."""
        if not self._validate_range():
            return
            
        try:
            start_time = self.start_spinbox.value()
            end_time = self.end_spinbox.value()
            
            # Show confirmation dialog
            num_sweeps = self.dataset.sweep_count()
            reply = QMessageBox.question(
                self, "Confirm Background Subtraction",
                f"Apply background subtraction to all {num_sweeps} sweeps?\n"
                f"Range: {start_time:.1f} - {end_time:.1f} ms\n\n"
                f"This will modify the dataset permanently.\n"
                f"To undo, you will need to reload the original file.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply != QMessageBox.StandardButton.Yes:
                return
            
            # Apply background subtraction to all sweeps
            processed_count = self._perform_background_subtraction(start_time, end_time)
            
            logger.info(f"Background subtraction applied: range [{start_time}, {end_time}] ms "
                       f"to {processed_count} sweeps")
            
            QMessageBox.information(
                self, "Success", 
                f"Background subtraction applied to {processed_count} sweeps.\n"
                f"Range: {start_time:.1f} - {end_time:.1f} ms"
            )
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Background subtraction failed: {e}")
            QMessageBox.critical(self, "Error", f"Background subtraction failed: {str(e)}")
            
    def _perform_background_subtraction(self, start_time: float, end_time: float) -> int:
        """
        Perform background subtraction on all sweeps in the dataset.
        
        Args:
            start_time: Start time of background range (ms)
            end_time: End time of background range (ms)
            
        Returns:
            int: Number of sweeps successfully processed
        """
        current_channel = self.channel_definitions.get_current_channel()
        processed_count = 0
        
        # Convert sweep indices to a list to avoid dictionary size changes during iteration
        sweep_indices = list(self.dataset.sweeps())
        
        for sweep_idx in sweep_indices:
            try:
                # Extract sweep data
                sweep_data = self.data_extractor.extract_sweep_data(self.dataset, sweep_idx)
                time_ms = sweep_data["time_ms"]
                current = sweep_data["current"]
                
                # Find background range indices
                mask = (time_ms >= start_time) & (time_ms <= end_time)
                if not np.any(mask):
                    logger.warning(f"No data in background range for sweep {sweep_idx}")
                    continue
                    
                # Calculate background average
                background_current = current[mask]
                background_avg = np.mean(background_current)
                
                # Subtract background from all current values
                corrected_current = current - background_avg
                
                # Get original sweep data to preserve structure
                original_sweep = self.dataset.get_sweep(sweep_idx)
                if original_sweep is None:
                    logger.warning(f"Could not retrieve original sweep {sweep_idx}")
                    continue
                    
                time_orig, data_matrix_orig = original_sweep
                
                # Create new data matrix with corrected current
                data_matrix_new = data_matrix_orig.copy()
                data_matrix_new[:, current_channel] = corrected_current
                
                # Update the sweep in the dataset
                self.dataset.add_sweep(sweep_idx, time_orig, data_matrix_new)
                
                processed_count += 1
                logger.debug(f"Applied background subtraction to sweep {sweep_idx}: "
                           f"avg = {background_avg:.3f} pA")
                
            except Exception as e:
                logger.error(f"Failed to process sweep {sweep_idx}: {e}")
                # Continue with other sweeps rather than failing entirely
                continue
                
        if processed_count == 0:
            raise Exception("No sweeps were successfully processed")
            
        return processed_count