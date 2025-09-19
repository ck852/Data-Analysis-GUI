"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

"""
Channel Toggle Switch Widget
A simple toggle switch for swapping channel assignments.
Place this file in: widgets/channel_toggle.py
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QSlider
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent

from data_analysis_gui.config.themes import MODERN_COLORS, BASE_FONT


class ToggleSlider(QSlider):
    """
    Custom QSlider subclass that toggles between two positions on click.
    Properly overrides mousePressEvent to handle toggle behavior.
    """

    def __init__(self, orientation=Qt.Orientation.Horizontal):
        super().__init__(orientation)
        self.setRange(0, 1)
        self.setValue(0)
        self.setPageStep(1)
        self.setSingleStep(1)
        self.setTickPosition(QSlider.TickPosition.NoTicks)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def mousePressEvent(self, event: QMouseEvent):
        """
        Override mouse press to toggle between states instead of jumping to position.
        """
        if self.isEnabled() and event.button() == Qt.MouseButton.LeftButton:
            # Toggle between 0 and 1
            current_value = self.value()
            new_value = 1 - current_value
            self.setValue(new_value)
            event.accept()
        else:
            # For other buttons or if disabled, use default behavior
            super().mousePressEvent(event)


class ChannelToggleSwitch(QWidget):
    """
    A simple toggle switch widget for channel assignment.
    Shows channel definitions stacked vertically next to the slider.
    """

    # Signal emitted when toggle state changes
    toggled = Signal(bool)  # True = swapped, False = normal

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_swapped = False
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        # Main horizontal layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)  # Reduced from (8, 4, 8, 4)
        layout.setSpacing(4)  # Reduced from 8

        # Create the custom toggle slider
        self.slider = ToggleSlider(Qt.Horizontal)
        self.slider.setFixedWidth(40)  # Reduced from 50
        self.slider.setFixedHeight(20)  # Reduced from 24

        # Style the slider to look like a toggle switch
        self._style_slider()

        # Create channel labels container
        label_container = QWidget()
        label_layout = QVBoxLayout(label_container)
        label_layout.setContentsMargins(0, 0, 0, 0)
        label_layout.setSpacing(1)  # Reduced from 2

        # Create channel labels with shorter text
        self.ch0_label = QLabel("Ch0: V")  # Shortened from "Ch. 0: Voltage"
        self.ch1_label = QLabel("Ch1: I")  # Shortened from "Ch. 1: Current"

        # Style labels with smaller font
        label_style = f"""
            QLabel {{
                color: {MODERN_COLORS['text']};
                {BASE_FONT}
                font-size: 9px;  
                font-weight: 500;
            }}
        """
        self.ch0_label.setStyleSheet(label_style)
        self.ch1_label.setStyleSheet(label_style)

        # Add labels to container
        label_layout.addWidget(self.ch0_label)
        label_layout.addWidget(self.ch1_label)

        # Add components to main layout
        layout.addWidget(self.slider)
        layout.addWidget(label_container)
        # Don't add stretch here to keep it compact

        # Connect slider signal
        self.slider.valueChanged.connect(self._on_slider_changed)

    def _style_slider(self):
        """Apply custom styling to make the slider look like a toggle switch."""
        # Define hover and pressed colors as slightly darker shades of primary
        primary_hover = "#0066CC"  # Darker blue for hover
        primary_pressed = "#0052A3"  # Even darker for pressed

        slider_style = f"""
            QSlider::groove:horizontal {{
                background: {MODERN_COLORS['surface']};
                height: 20px;
                border-radius: 10px;
                border: 1px solid {MODERN_COLORS['border']};
            }}
            
            QSlider::handle:horizontal {{
                background: {MODERN_COLORS['primary']};
                border: 1px solid {primary_hover};
                width: 18px;
                height: 18px;
                margin: -1px 0;
                border-radius: 9px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {primary_hover};
                border: 1px solid {primary_pressed};
            }}
            
            QSlider::handle:horizontal:pressed {{
                background: {primary_pressed};
            }}
            
            QSlider:disabled {{
                opacity: 0.5;
            }}
        """
        self.slider.setStyleSheet(slider_style)

    def _on_slider_changed(self, value):
        """Handle slider value changes."""
        self.is_swapped = value == 1
        self._update_labels()
        self.toggled.emit(self.is_swapped)

    def _update_labels(self):
        """Update channel labels based on current state."""
        if self.is_swapped:
            self.ch0_label.setText("Ch. 0: Current")
            self.ch1_label.setText("Ch. 1: Voltage")
        else:
            self.ch0_label.setText("Ch. 0: Voltage")
            self.ch1_label.setText("Ch. 1: Current")

    def set_swapped(self, swapped):
        """
        Set the toggle state programmatically.

        Args:
            swapped: True if channels should be swapped, False otherwise
        """
        self.slider.setValue(1 if swapped else 0)
        # Note: This will trigger _on_slider_changed via signal

    def set_enabled(self, enabled):
        """Enable or disable the toggle switch."""
        self.slider.setEnabled(enabled)
        # Update label appearance when disabled
        if enabled:
            color = MODERN_COLORS["text"]
        else:
            color = MODERN_COLORS["text_muted"]

        label_style = f"""
            QLabel {{
                color: {color};
                {BASE_FONT}
                font-size: 11px;
                font-weight: 500;
            }}
        """
        self.ch0_label.setStyleSheet(label_style)
        self.ch1_label.setStyleSheet(label_style)
