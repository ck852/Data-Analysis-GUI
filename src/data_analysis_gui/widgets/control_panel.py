"""
Control Panel Widget - PHASE 4 REFACTORED with Full Theme Integration
Handles all control settings and communicates via signals.
Now fully utilizes themes.py for consistent modern styling.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QScrollArea, QGroupBox,
                             QLabel, QPushButton, QCheckBox,
                             QGridLayout)
from PyQt5.QtCore import pyqtSignal

# Import custom widgets that handle scrolling properly
from data_analysis_gui.widgets.custom_inputs import SelectAllSpinBox, NoScrollComboBox
from data_analysis_gui.config import DEFAULT_SETTINGS
from data_analysis_gui.core.params import AnalysisParameters

from data_analysis_gui.config.themes import (
    style_button, style_scroll_area, style_group_box, style_label,
    style_checkbox, apply_compact_layout,
    style_spinbox_with_arrows, style_combo_simple,  # New styling functions
    MODERN_COLORS, SPACING, WIDGET_SIZES
)

class ControlPanel(QWidget):
    """
    Self-contained control panel widget that manages all analysis settings.
    Emits signals to communicate user actions to the main window.
    
    PHASE 4: Now creates AnalysisParameters objects directly,
    eliminating the dictionary intermediate step for type safety.
    Fully themed using themes.py functions.
    """

    # Define signals for communication with main window
    analysis_requested = pyqtSignal()  # User wants to generate analysis plot
    export_requested = pyqtSignal()  # User wants to export data

    dual_range_toggled = pyqtSignal(bool)  # Dual range checkbox changed
    range_values_changed = pyqtSignal()  # Any range spinbox value changed

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_swapped = False
        self._pending_swap_state = False
        
        # Dictionary to track previous valid values
        self._previous_valid_values = {}
        
        # Track which fields have invalid state
        self._invalid_fields = set()
        
        # Store original style sheets for restoration
        self._original_styles = {}
        
        self._setup_ui()
        
        # Initialize tracking with starting values after UI setup
        self._previous_valid_values = {
            'start1': self.start_spin.value(),
            'end1': self.end_spin.value(),
            'start2': self.start_spin2.value(),
            'end2': self.end_spin2.value()
        }
        
        # Store original styles for all spinboxes after themes are applied
        self._original_styles = {
            'start1': self.start_spin.styleSheet(),
            'end1': self.end_spin.styleSheet(),
            'start2': self.start_spin2.styleSheet(),
            'end2': self.end_spin2.styleSheet()
        }
        
        self._connect_signals()

    def _setup_ui(self):
        """Set up the control panel UI with full theme integration"""
        # Create scroll area for the controls
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumWidth(400)
        
        # Apply theme styling to scroll area
        style_scroll_area(scroll_area)

        # Main control widget inside scroll area
        control_widget = QWidget()
        scroll_area.setWidget(control_widget)

        # Layout for control widget with theme-based compact spacing
        layout = QVBoxLayout(control_widget)
        apply_compact_layout(control_widget, spacing=8, margin=8)

        # Add all control groups
        layout.addWidget(self._create_analysis_settings_group())
        layout.addWidget(self._create_plot_settings_group())

        # Export Plot Data button with theme styling
        self.export_plot_btn = QPushButton("Export Analysis Data")
        style_button(self.export_plot_btn, "secondary")
        self.export_plot_btn.clicked.connect(self.export_requested.emit)
        self.export_plot_btn.setEnabled(False)
        layout.addWidget(self.export_plot_btn)

        # Small spacing at bottom
        layout.addSpacing(10)

        # Set main layout for this widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

    def _create_analysis_settings_group(self):
        """Create the analysis settings group with full theme styling"""
        analysis_group = QGroupBox("Analysis Settings")
        style_group_box(analysis_group)
        
        analysis_layout = QGridLayout(analysis_group)
        apply_compact_layout(analysis_group, spacing=6, margin=8)

        # Range 1 settings
        self._add_range1_settings(analysis_layout)

        # Dual range checkbox with theme styling
        self.dual_range_cb = QCheckBox("Use Dual Analysis")
        style_checkbox(self.dual_range_cb)
        self.dual_range_cb.stateChanged.connect(self._on_dual_range_changed)
        analysis_layout.addWidget(self.dual_range_cb, 2, 0, 1, 2)

        # Range 2 settings
        self._add_range2_settings(analysis_layout)

        # Stimulus period
        stim_label = QLabel("Stimulus Period (ms):")
        style_label(stim_label, 'normal')
        analysis_layout.addWidget(stim_label, 5, 0)
        
        self.period_spin = SelectAllSpinBox()
        self.period_spin.setRange(1, 100000)
        self.period_spin.setValue(DEFAULT_SETTINGS['stimulus_period'])
        self.period_spin.setSingleStep(100)
        self.period_spin.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_spinbox_with_arrows(self.period_spin)  # Use new styling function
        analysis_layout.addWidget(self.period_spin, 5, 1)

        return analysis_group

    def _add_range1_settings(self, layout):
        """Add Range 1 settings to layout with theme styling"""
        # Range 1 Start
        start_label = QLabel("Range 1 Start (ms):")
        style_label(start_label, 'normal')
        layout.addWidget(start_label, 0, 0)
        
        self.start_spin = SelectAllSpinBox()
        self.start_spin.setRange(0, 100000)
        self.start_spin.setValue(DEFAULT_SETTINGS['range1_start'])
        self.start_spin.setSingleStep(0.05)
        self.start_spin.setDecimals(2)
        self.start_spin.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_spinbox_with_arrows(self.start_spin)  # Use new styling function
        layout.addWidget(self.start_spin, 0, 1)

        # Range 1 End
        end_label = QLabel("Range 1 End (ms):")
        style_label(end_label, 'normal')
        layout.addWidget(end_label, 1, 0)
        
        self.end_spin = SelectAllSpinBox()
        self.end_spin.setRange(0, 100000)
        self.end_spin.setValue(DEFAULT_SETTINGS['range1_end'])
        self.end_spin.setSingleStep(0.05)
        self.end_spin.setDecimals(2)
        self.end_spin.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_spinbox_with_arrows(self.end_spin)  # Use new styling function
        layout.addWidget(self.end_spin, 1, 1)

    def _add_range2_settings(self, layout):
        """Add Range 2 settings to layout with theme styling"""
        # Range 2 Start
        start2_label = QLabel("Range 2 Start (ms):")
        style_label(start2_label, 'normal')
        layout.addWidget(start2_label, 3, 0)
        
        self.start_spin2 = SelectAllSpinBox()
        self.start_spin2.setRange(0, 100000)
        self.start_spin2.setValue(DEFAULT_SETTINGS['range2_start'])
        self.start_spin2.setSingleStep(0.05)
        self.start_spin2.setDecimals(2)
        self.start_spin2.setEnabled(False)
        self.start_spin2.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_spinbox_with_arrows(self.start_spin2)  # Use new styling function
        layout.addWidget(self.start_spin2, 3, 1)

        # Range 2 End
        end2_label = QLabel("Range 2 End (ms):")
        style_label(end2_label, 'normal')
        layout.addWidget(end2_label, 4, 0)
        
        self.end_spin2 = SelectAllSpinBox()
        self.end_spin2.setRange(0, 100000)
        self.end_spin2.setValue(DEFAULT_SETTINGS['range2_end'])
        self.end_spin2.setSingleStep(0.05)
        self.end_spin2.setDecimals(2)
        self.end_spin2.setEnabled(False)
        self.end_spin2.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_spinbox_with_arrows(self.end_spin2)  # Use new styling function
        layout.addWidget(self.end_spin2, 4, 1)

    def _create_plot_settings_group(self):
        """Create the plot settings group with full theme styling"""
        plot_group = QGroupBox("Plot Settings")
        style_group_box(plot_group)
        
        plot_layout = QGridLayout(plot_group)
        apply_compact_layout(plot_group, spacing=6, margin=8)

        # X-axis settings with NoScrollComboBox
        x_label = QLabel("X-Axis:")
        style_label(x_label, 'normal')
        plot_layout.addWidget(x_label, 0, 0)
        
        self.x_measure_combo = NoScrollComboBox()  # Use NoScrollComboBox
        self.x_measure_combo.addItems(["Time", "Peak", "Average"])
        self.x_measure_combo.setCurrentText("Average")
        self.x_measure_combo.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_combo_simple(self.x_measure_combo)  # Use new simple styling
        plot_layout.addWidget(self.x_measure_combo, 0, 1)

        self.x_channel_combo = NoScrollComboBox()  # Use NoScrollComboBox
        self.x_channel_combo.addItems(["Voltage", "Current"])
        self.x_channel_combo.setCurrentText("Voltage")
        self.x_channel_combo.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_combo_simple(self.x_channel_combo)  # Use new simple styling
        plot_layout.addWidget(self.x_channel_combo, 0, 2)

        # Y-axis settings with NoScrollComboBox
        y_label = QLabel("Y-Axis:")
        style_label(y_label, 'normal')
        plot_layout.addWidget(y_label, 1, 0)
        
        self.y_measure_combo = NoScrollComboBox()  # Use NoScrollComboBox
        self.y_measure_combo.addItems(["Peak", "Average", "Time"])
        self.y_measure_combo.setCurrentText("Average")
        self.y_measure_combo.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_combo_simple(self.y_measure_combo)  # Use new simple styling
        plot_layout.addWidget(self.y_measure_combo, 1, 1)

        self.y_channel_combo = NoScrollComboBox()  # Use NoScrollComboBox
        self.y_channel_combo.addItems(["Voltage", "Current"])
        self.y_channel_combo.setCurrentText("Current")
        self.y_channel_combo.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_combo_simple(self.y_channel_combo)  # Use new simple styling
        plot_layout.addWidget(self.y_channel_combo, 1, 2)

        # Update plot button with theme styling
        self.update_plot_btn = QPushButton("Generate Analysis Plot")
        style_button(self.update_plot_btn, "primary")
        self.update_plot_btn.clicked.connect(self.analysis_requested.emit)
        self.update_plot_btn.setEnabled(False)
        plot_layout.addWidget(self.update_plot_btn, 2, 0, 1, 3)

        # Peak Mode settings with NoScrollComboBox
        peak_label = QLabel("Peak Mode:")
        style_label(peak_label, 'normal')
        plot_layout.addWidget(peak_label, 3, 0)
        
        self.peak_mode_combo = NoScrollComboBox()  # Use NoScrollComboBox
        self.peak_mode_combo.addItems(["Absolute", "Positive", "Negative", "Peak-Peak"])
        self.peak_mode_combo.setCurrentText("Absolute")
        self.peak_mode_combo.setToolTip("Peak calculation mode (applies when X or Y axis is set to Peak)")
        self.peak_mode_combo.setMinimumHeight(WIDGET_SIZES['input_height'])
        style_combo_simple(self.peak_mode_combo)  # Use new simple styling
        plot_layout.addWidget(self.peak_mode_combo, 3, 1, 1, 2)

        # Connect signal to enable/disable peak mode based on axis selection
        self.x_measure_combo.currentTextChanged.connect(self._update_peak_mode_visibility)
        self.y_measure_combo.currentTextChanged.connect(self._update_peak_mode_visibility)

        return plot_group

    def _update_peak_mode_visibility(self):
        """Enable/disable peak mode combo based on whether Peak is selected"""
        is_peak_selected = (self.x_measure_combo.currentText() == "Peak" or
                        self.y_measure_combo.currentText() == "Peak")
        self.peak_mode_combo.setEnabled(is_peak_selected)
        
        # Update visual state when disabled
        if not is_peak_selected:
            # Re-apply combo box styling to ensure disabled state looks correct
            style_combo_simple(self.peak_mode_combo)

    def _connect_signals(self):
        """Connect internal widget signals with validation."""
        # Validate on any value change
        self.start_spin.valueChanged.connect(self._validate_and_update)
        self.end_spin.valueChanged.connect(self._validate_and_update)
        self.start_spin2.valueChanged.connect(self._validate_and_update)
        self.end_spin2.valueChanged.connect(self._validate_and_update)
        # Also re-validate when the dual range checkbox is toggled
        self.dual_range_cb.stateChanged.connect(self._validate_and_update)

    def _validate_and_update(self):
        """
        Validates all ranges, updates UI feedback, and emits a signal
        that the range values have changed for the plot to sync.
        """
        # --- Validate Range 1 ---
        start1_val = self.start_spin.value()
        end1_val = self.end_spin.value()
        is_range1_valid = end1_val > start1_val

        if not is_range1_valid:
            self._mark_field_invalid('start1')
            self._mark_field_invalid('end1')
        else:
            self._clear_invalid_state('start1')
            self._clear_invalid_state('end1')

        # --- Validate Range 2 (if enabled) ---
        is_range2_valid = True
        if self.dual_range_cb.isChecked():
            start2_val = self.start_spin2.value()
            end2_val = self.end_spin2.value()
            is_range2_valid = end2_val > start2_val

            if not is_range2_valid:
                self._mark_field_invalid('start2')
                self._mark_field_invalid('end2')
            else:
                self._clear_invalid_state('start2')
                self._clear_invalid_state('end2')
        else:
            # If dual range is disabled, its fields can't be invalid
            self._clear_invalid_state('start2')
            self._clear_invalid_state('end2')

        # --- Update Button State ---
        is_all_valid = is_range1_valid and is_range2_valid
        
        # Only enable buttons if controls are generally active
        if self.update_plot_btn.property("enabled_by_file"):
            self.update_plot_btn.setEnabled(is_all_valid)
            self.export_plot_btn.setEnabled(is_all_valid)

        # --- Sync Cursors ---
        self.range_values_changed.emit()

    def _mark_field_invalid(self, spinbox_key: str):
        """Mark a field as invalid using theme functions."""
        spinbox_map = {
            'start1': self.start_spin,
            'end1': self.end_spin,
            'start2': self.start_spin2,
            'end2': self.end_spin2
        }
        spinbox = spinbox_map.get(spinbox_key)
        if spinbox and spinbox_key not in self._invalid_fields:
            self._invalid_fields.add(spinbox_key)
            # Save the current style before applying invalid state
            if spinbox_key not in self._original_styles:
                self._original_styles[spinbox_key] = spinbox.styleSheet()
            
            # Apply invalid background color from theme
            current_style = spinbox.styleSheet()
            invalid_style = f"{current_style}\nQDoubleSpinBox {{ background-color: {MODERN_COLORS['invalid_bg']}; border-color: {MODERN_COLORS['danger']}; }}"
            spinbox.setStyleSheet(invalid_style)

    def _clear_invalid_state(self, spinbox_key: str):
        """Clear the invalid state from a field using theme functions."""
        if spinbox_key in self._invalid_fields:
            self._invalid_fields.remove(spinbox_key)
            spinbox_map = {
                'start1': self.start_spin,
                'end1': self.end_spin,
                'start2': self.start_spin2,
                'end2': self.end_spin2
            }
            spinbox = spinbox_map.get(spinbox_key)
            if spinbox:
                # Restore the original styled state
                style_spinbox_with_arrows(spinbox)

    def _on_dual_range_changed(self):
        """Handle dual range checkbox state change."""
        enabled = self.dual_range_cb.isChecked()
        self.start_spin2.setEnabled(enabled)
        self.end_spin2.setEnabled(enabled)
        
        # Re-apply styling to ensure disabled state looks correct
        style_spinbox_with_arrows(self.start_spin2)
        style_spinbox_with_arrows(self.end_spin2)
        
        self.dual_range_toggled.emit(enabled)
        # The validation is handled by the connected signal

    def set_controls_enabled(self, enabled: bool):
        """Enable or disable analysis controls based on file loading."""
        # Use a custom property to track if buttons *should* be enabled
        self.update_plot_btn.setProperty("enabled_by_file", enabled)
        self.export_plot_btn.setProperty("enabled_by_file", enabled)

        if enabled:
            # If enabling, run validation to set the correct state of the buttons
            self._validate_and_update()
            if self._pending_swap_state:
                self._is_swapped = self._pending_swap_state
                self._pending_swap_state = False
        else:
            # If disabling, just turn them off
            self.update_plot_btn.setEnabled(False)
            self.export_plot_btn.setEnabled(False)

    # --- PHASE 4: New method to create AnalysisParameters directly ---
    
    def get_parameters(self) -> AnalysisParameters:
        """
        Get analysis parameters as a proper typed object.
        
        Returns:
            AnalysisParameters object with current control values
        """
        from data_analysis_gui.core.params import AnalysisParameters, AxisConfig
        
        # Determine peak mode
        peak_mode = self.peak_mode_combo.currentText()
        
        # Create X-axis config
        x_measure = self.x_measure_combo.currentText()
        x_axis = AxisConfig(
            measure=x_measure,
            channel=self.x_channel_combo.currentText() if x_measure != "Time" else None,
            peak_type=peak_mode if x_measure == "Peak" else None
        )
        
        # Create Y-axis config
        y_measure = self.y_measure_combo.currentText()
        y_axis = AxisConfig(
            measure=y_measure,
            channel=self.y_channel_combo.currentText() if y_measure != "Time" else None,
            peak_type=peak_mode if y_measure == "Peak" else None
        )
        
        # Return clean parameters object
        return AnalysisParameters(
            range1_start=self.start_spin.value(),
            range1_end=self.end_spin.value(),
            use_dual_range=self.dual_range_cb.isChecked(),
            range2_start=self.start_spin2.value() if self.dual_range_cb.isChecked() else None,
            range2_end=self.end_spin2.value() if self.dual_range_cb.isChecked() else None,
            stimulus_period=self.period_spin.value(),
            x_axis=x_axis,
            y_axis=y_axis,
            channel_config={'channels_swapped': self._is_swapped}
        )

    # --- Public methods for data access and updates ---

    def get_range_values(self) -> dict:
        """Get current range values"""
        return {
            'range1_start': self.start_spin.value(),
            'range1_end': self.end_spin.value(),
            'use_dual_range': self.dual_range_cb.isChecked(),
            'range2_start': self.start_spin2.value() if self.dual_range_cb.isChecked() else None,
            'range2_end': self.end_spin2.value() if self.dual_range_cb.isChecked() else None
        }

    def get_range_spinboxes(self) -> dict:
        """Get references to range spinboxes for plot manager"""
        spinboxes = {
            'start1': self.start_spin,
            'end1': self.end_spin
        }
        if self.dual_range_cb.isChecked():
            spinboxes['start2'] = self.start_spin2
            spinboxes['end2'] = self.end_spin2
        return spinboxes

    def update_range_value(self, spinbox_key: str, value: float):
        """Update a specific range spinbox value (e.g., from cursor drag)."""
        spinbox_map = {
            'start1': self.start_spin,
            'end1': self.end_spin,
            'start2': self.start_spin2,
            'end2': self.end_spin2
        }
        if spinbox_key in spinbox_map:
            # setValue() triggers validation automatically
            spinbox_map[spinbox_key].setValue(value)

    def set_analysis_range(self, max_time: float):
        """Sets the maximum value for the analysis range spinboxes and clamps current values."""
        self.start_spin.setRange(0, max_time)
        self.end_spin.setRange(0, max_time)
        self.start_spin2.setRange(0, max_time)
        self.end_spin2.setRange(0, max_time)

        # Clamp existing values to the new range
        if self.start_spin.value() > max_time:
            self.start_spin.setValue(max_time)
        if self.end_spin.value() > max_time:
            self.end_spin.setValue(max_time)
        if self.start_spin2.value() > max_time:
            self.start_spin2.setValue(max_time)
        if self.end_spin2.value() > max_time:
            self.end_spin2.setValue(max_time)
            
        # After clamping, sync the valid state
        self._previous_valid_values = {
            'start1': self.start_spin.value(),
            'end1': self.end_spin.value(),
            'start2': self.start_spin2.value(),
            'end2': self.end_spin2.value()
        }

    def get_pending_swap_state(self) -> bool:
        """
        Get the pending swap state that should be applied when a file is loaded.
        """
        return self._pending_swap_state

    def clear_pending_swap_state(self):
        """Clear the pending swap state after it's been applied."""
        self._pending_swap_state = False