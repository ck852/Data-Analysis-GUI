"""
PatchBatch Electrophysiology Data Analysis Tool

Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)

Enhanced GUI input widgets for improved user experience.

This module provides custom Qt widget subclasses that enhance the default behavior
of standard input controls. These widgets improve usability by providing automatic
text selection, preventing accidental value changes from mouse wheel events, and
other user-friendly behaviors.

Classes:
    - SelectAllLineEdit: QLineEdit with automatic text selection on focus
    - SelectAllSpinBox: QDoubleSpinBox with text selection and wheel event blocking  
    - SelectAllIntSpinBox: QSpinBox with text selection and wheel event blocking
    - NoScrollComboBox: QComboBox that ignores mouse wheel events

Features:
    - Automatic text selection for faster data entry
    - Mouse wheel event blocking to prevent accidental changes
    - Consistent behavior across different input widget types
    - Drop-in replacements for standard Qt input widgets
"""

from PySide6.QtWidgets import QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox
from PySide6.QtCore import QTimer


class SelectAllLineEdit(QLineEdit):
    """
    QLineEdit subclass that automatically selects all text when it gains focus.

    Features:
        - Selects all text on focus-in unless suppressed.
        - Provides a method to set focus without selecting all text.
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the SelectAllLineEdit.

        Args:
            *args: Positional arguments for QLineEdit.
            **kwargs: Keyword arguments for QLineEdit.
        """
        super().__init__(*args, **kwargs)
        self._select_all_on_focus = True

    def focusInEvent(self, event):
        """
        Handle focus-in event, selecting all text if enabled.

        Args:
            event: QFocusEvent
        """
        super().focusInEvent(event)
        if self._select_all_on_focus:
            QTimer.singleShot(0, self.selectAll)
        # Reset the flag after the event is handled
        self._select_all_on_focus = True

    def setFocusAndDoNotSelect(self):
        """
        Set focus to the widget without triggering select-all behavior.
        """
        self._select_all_on_focus = False
        self.setFocus()


class SelectAllSpinBox(QDoubleSpinBox):
    """
    QDoubleSpinBox subclass that selects all text when focused and ignores wheel events.

    Features:
        - Selects all text on focus-in.
        - Ignores mouse wheel events to prevent accidental value changes.
    """

    def focusInEvent(self, event):
        """
        Handle focus-in event, selecting all text.

        Args:
            event: QFocusEvent
        """
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)

    def wheelEvent(self, event):
        """
        Ignore mouse wheel events.

        Args:
            event: QWheelEvent
        """
        event.ignore()


class SelectAllIntSpinBox(QSpinBox):
    """
    QSpinBox subclass that selects all text when focused and ignores wheel events.

    Features:
        - Selects all text on focus-in.
        - Ignores mouse wheel events to prevent accidental value changes.
    """

    def focusInEvent(self, event):
        """
        Handle focus-in event, selecting all text.

        Args:
            event: QFocusEvent
        """
        super().focusInEvent(event)
        QTimer.singleShot(0, self.selectAll)

    def wheelEvent(self, event):
        """
        Ignore mouse wheel events.

        Args:
            event: QWheelEvent
        """
        event.ignore()


class NoScrollComboBox(QComboBox):
    """
    QComboBox subclass that ignores mouse wheel events to prevent accidental selection changes.
    """

    def wheelEvent(self, event):
        """
        Ignore mouse wheel events.

        Args:
            event: QWheelEvent
        """
        event.ignore()
