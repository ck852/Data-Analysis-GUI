# config/themes.py
"""
Modern theme system for the Data Analysis GUI.
Provides consistent styling across all windows and dialogs.
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QWidget, QPushButton, QApplication
from PyQt5.QtCore import Qt

# Color palette based on modern design principles
MODERN_COLORS = {
    # Primary colors
    'primary': '#0084FF',
    'primary_hover': '#0066CC',
    'primary_pressed': '#0052A3',
    
    # Accent colors (success/go actions)
    'accent': '#28A745',
    'accent_hover': '#218838',
    'accent_pressed': '#1E7E34',
    
    # Secondary colors
    'secondary': '#F8F9FA',
    'secondary_text': '#495057',
    'secondary_border': '#DEE2E6',
    'secondary_hover': '#E9ECEF',
    'secondary_hover_border': '#ADB5BD',
    'secondary_pressed': '#DEE2E6',
    
    # Danger/warning colors
    'danger': '#DC3545',
    'danger_hover': '#C82333',
    'warning': '#FFC107',
    'warning_hover': '#E0A800',
    
    # UI element colors
    'background': '#FFFFFF',
    'surface': '#F8F9FA',
    'border': '#DEE2E6',
    'border_focus': '#80BDFF',
    'text': '#212529',
    'text_muted': '#6C757D',
    'text_light': '#777777',
    'disabled_bg': '#CCCCCC',
    'disabled_text': '#888888',
    
    # List/table colors
    'list_hover': '#F5F5F5',
    'list_selected': '#E3F2FD',
    'list_selected_text': '#1976D2',
    'list_border': '#F0F0F0',
    
    # Special elements
    'progress_bg': '#E9ECEF',
    'progress_chunk': '#0084FF',
    'separator': '#E0E0E0',
}

# Typography settings
TYPOGRAPHY = {
    'font_family': 'Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif',
    'font_size_base': '20px',
    'font_size_small': '20px',
    'font_size_large': '23px',
    'font_weight_normal': '400',
    'font_weight_medium': '500',
    'font_weight_bold': '600',
    'line_height': '1.5',
}

# Spacing and sizing
SPACING = {
    'padding_xs': '2px',
    'padding_sm': '4px',
    'padding_md': '8px',
    'padding_lg': '12px',
    'margin_xs': '2px',
    'margin_sm': '4px',
    'margin_md': '8px',
    'margin_lg': '12px',
    'border_radius': '3px',
    'border_radius_lg': '4px',
}

def get_button_style(style_type: str = "secondary") -> str:
    """
    Get button stylesheet for different button types.
    
    Args:
        style_type: 'primary', 'accent', 'secondary', 'danger', or 'warning'
    
    Returns:
        Stylesheet string for QPushButton
    """
    if style_type == "primary":
        return f"""
            QPushButton {{
                background-color: {MODERN_COLORS['primary']};
                color: white;
                border: none;
                border-radius: {SPACING['border_radius']};
                padding: 6px 16px;
                font-size: {TYPOGRAPHY['font_size_base']};
                font-weight: {TYPOGRAPHY['font_weight_medium']};
                font-family: {TYPOGRAPHY['font_family']};
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['primary_hover']};
            }}
            QPushButton:pressed {{
                background-color: {MODERN_COLORS['primary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {MODERN_COLORS['disabled_bg']};
                color: {MODERN_COLORS['disabled_text']};
            }}
        """
    
    elif style_type == "accent":
        return f"""
            QPushButton {{
                background-color: {MODERN_COLORS['accent']};
                color: white;
                border: none;
                border-radius: {SPACING['border_radius']};
                padding: 6px 16px;
                font-size: {TYPOGRAPHY['font_size_base']};
                font-weight: {TYPOGRAPHY['font_weight_medium']};
                font-family: {TYPOGRAPHY['font_family']};
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['accent_hover']};
            }}
            QPushButton:pressed {{
                background-color: {MODERN_COLORS['accent_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {MODERN_COLORS['disabled_bg']};
                color: {MODERN_COLORS['disabled_text']};
            }}
        """
    
    elif style_type == "danger":
        return f"""
            QPushButton {{
                background-color: {MODERN_COLORS['danger']};
                color: white;
                border: none;
                border-radius: {SPACING['border_radius']};
                padding: 6px 16px;
                font-size: {TYPOGRAPHY['font_size_base']};
                font-weight: {TYPOGRAPHY['font_weight_medium']};
                font-family: {TYPOGRAPHY['font_family']};
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['danger_hover']};
            }}
            QPushButton:pressed {{
                background-color: #BD2130;
            }}
            QPushButton:disabled {{
                background-color: {MODERN_COLORS['disabled_bg']};
                color: {MODERN_COLORS['disabled_text']};
            }}
        """
    
    else:  # secondary (default)
        return f"""
            QPushButton {{
                background-color: {MODERN_COLORS['secondary']};
                color: {MODERN_COLORS['secondary_text']};
                border: 1px solid {MODERN_COLORS['secondary_border']};
                border-radius: {SPACING['border_radius']};
                padding: 6px 16px;
                font-size: {TYPOGRAPHY['font_size_base']};
                font-family: {TYPOGRAPHY['font_family']};
            }}
            QPushButton:hover {{
                background-color: {MODERN_COLORS['secondary_hover']};
                border-color: {MODERN_COLORS['secondary_hover_border']};
            }}
            QPushButton:pressed {{
                background-color: {MODERN_COLORS['secondary_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {MODERN_COLORS['secondary']};
                color: {MODERN_COLORS['secondary_hover_border']};
                border-color: {MODERN_COLORS['secondary_hover']};
            }}
        """

def get_dialog_stylesheet() -> str:
    """Get the complete stylesheet for dialogs."""
    return f"""
        QDialog {{
            background-color: {MODERN_COLORS['background']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        
        QMainWindow {{
            background-color: {MODERN_COLORS['background']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        
        QWidget {{
            font-family: {TYPOGRAPHY['font_family']};
        }}
        
        QLabel {{
            color: {MODERN_COLORS['text']};
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        
        QGroupBox {{
            font-weight: {TYPOGRAPHY['font_weight_medium']};
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius_lg']};
            margin-top: 8px;
            padding-top: 8px;
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px;
            color: {MODERN_COLORS['text']};
        }}
        
        QListWidget {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius_lg']};
            background-color: {MODERN_COLORS['background']};
            padding: {SPACING['padding_xs']};
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        
        QListWidget::item {{
            padding: 2px 4px;
            border-bottom: 1px solid {MODERN_COLORS['list_border']};
        }}
        
        QListWidget::item:selected {{
            background-color: {MODERN_COLORS['list_selected']};
            color: {MODERN_COLORS['list_selected_text']};
        }}
        
        QListWidget::item:hover {{
            background-color: {MODERN_COLORS['list_hover']};
        }}
        
        QTableWidget {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            background-color: {MODERN_COLORS['background']};
            gridline-color: {MODERN_COLORS['list_border']};
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        
        QTableWidget::item {{
            padding: {SPACING['padding_sm']};
        }}
        
        QTableWidget::item:selected {{
            background-color: {MODERN_COLORS['list_selected']};
            color: {MODERN_COLORS['list_selected_text']};
        }}
        
        QHeaderView::section {{
            background-color: {MODERN_COLORS['surface']};
            border: none;
            border-bottom: 2px solid {MODERN_COLORS['border']};
            padding: {SPACING['padding_sm']} {SPACING['padding_md']};
            font-weight: {TYPOGRAPHY['font_weight_medium']};
        }}
        
        QProgressBar {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            text-align: center;
            font-size: {TYPOGRAPHY['font_size_small']};
            background-color: {MODERN_COLORS['progress_bg']};
        }}
        
        QProgressBar::chunk {{
            background-color: {MODERN_COLORS['progress_chunk']};
            border-radius: 2px;
        }}
        
        QCheckBox {{
            spacing: 4px;
            font-size: {TYPOGRAPHY['font_size_base']};
            color: {MODERN_COLORS['text']};
        }}
        
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: 2px;
            background-color: {MODERN_COLORS['background']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {MODERN_COLORS['primary']};
            border-color: {MODERN_COLORS['primary']};
        }}
        
        QComboBox {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: 4px 8px;
            background-color: {MODERN_COLORS['background']};
            font-size: {TYPOGRAPHY['font_size_base']};
            min-height: 28px;
        }}
        
        QComboBox:hover {{
            border-color: {MODERN_COLORS['secondary_hover_border']};
        }}
        
        QComboBox:focus {{
            border-color: {MODERN_COLORS['border_focus']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 5px solid {MODERN_COLORS['text_muted']};
            margin-right: 5px;
        }}
        
        QSpinBox, QDoubleSpinBox {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: 4px 8px;
            background-color: {MODERN_COLORS['background']};
            font-size: {TYPOGRAPHY['font_size_base']};
            min-height: 28px;
        }}
        
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {MODERN_COLORS['secondary_hover_border']};
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {MODERN_COLORS['border_focus']};
        }}
        
        QLineEdit {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: 4px 8px;
            background-color: {MODERN_COLORS['background']};
            font-size: {TYPOGRAPHY['font_size_base']};
            min-height: 28px;
        }}
        
        QLineEdit:hover {{
            border-color: {MODERN_COLORS['secondary_hover_border']};
        }}
        
        QLineEdit:focus {{
            border-color: {MODERN_COLORS['border_focus']};
        }}
        
        QScrollBar:vertical {{
            background: {MODERN_COLORS['surface']};
            width: 12px;
            border: none;
        }}
        
        QScrollBar::handle:vertical {{
            background: {MODERN_COLORS['secondary_hover_border']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background: {MODERN_COLORS['text_muted']};
        }}
        
        QScrollBar:horizontal {{
            background: {MODERN_COLORS['surface']};
            height: 12px;
            border: none;
        }}
        
        QScrollBar::handle:horizontal {{
            background: {MODERN_COLORS['secondary_hover_border']};
            border-radius: 6px;
            min-width: 20px;
        }}
        
        QScrollBar::handle:horizontal:hover {{
            background: {MODERN_COLORS['text_muted']};
        }}
        
        QSplitter::handle {{
            background: {MODERN_COLORS['border']};
        }}
        
        QSplitter::handle:hover {{
            background: {MODERN_COLORS['secondary_hover_border']};
        }}
        
        QStatusBar {{
            background-color: {MODERN_COLORS['surface']};
            border-top: 1px solid {MODERN_COLORS['border']};
            font-size: {TYPOGRAPHY['font_size_small']};
            color: {MODERN_COLORS['text_muted']};
        }}
        
        QToolBar {{
            background-color: {MODERN_COLORS['surface']};
            border-bottom: 1px solid {MODERN_COLORS['border']};
            padding: 2px;
            spacing: 2px;
        }}
        
        QToolBar::separator {{
            background-color: {MODERN_COLORS['separator']};
            width: 1px;
            margin: 4px 6px;
        }}
        
        QToolButton {{
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: {SPACING['border_radius']};
            padding: 4px;
            margin: 1px;
        }}
        
        QToolButton:hover {{
            background-color: {MODERN_COLORS['secondary_hover']};
            border: 1px solid {MODERN_COLORS['border']};
        }}
        
        QToolButton:pressed {{
            background-color: {MODERN_COLORS['secondary_pressed']};
        }}
        
        QToolButton:checked {{
            background-color: {MODERN_COLORS['list_selected']};
            border: 1px solid {MODERN_COLORS['primary']};
        }}
        
        QFrame[frameShape="4"] /* HLine */ {{
            color: {MODERN_COLORS['separator']};
            max-height: 1px;
        }}
        
        QFrame[frameShape="5"] /* VLine */ {{
            color: {MODERN_COLORS['separator']};
            max-width: 1px;
        }}
    """

def apply_modern_style(widget: QWidget) -> None:
    """
    Apply modern styling to a widget and all its children.
    
    Args:
        widget: The widget to style (QDialog, QMainWindow, or any QWidget)
    """
    widget.setStyleSheet(get_dialog_stylesheet())

def style_button(button: QPushButton, style_type: str = "secondary") -> None:
    """
    Apply modern styling to a specific button.
    
    Args:
        button: The button to style
        style_type: 'primary', 'accent', 'secondary', 'danger', or 'warning'
    """
    button.setStyleSheet(get_button_style(style_type))

def apply_compact_layout(widget: QWidget) -> None:
    """
    Apply compact spacing to a widget's layout.
    
    Args:
        widget: The widget whose layout should be made compact
    """
    if widget.layout():
        widget.layout().setSpacing(8)
        widget.layout().setContentsMargins(12, 12, 12, 12)

def create_styled_button(text: str, style_type: str = "secondary", 
                        parent: QWidget = None) -> QPushButton:
    """
    Create a new button with modern styling.
    
    Args:
        text: Button text
        style_type: 'primary', 'accent', 'secondary', 'danger', or 'warning'
        parent: Optional parent widget
    
    Returns:
        Styled QPushButton
    """
    button = QPushButton(text, parent)
    style_button(button, style_type)
    return button

def apply_theme_to_application(app: QApplication) -> None:
    """
    Apply the modern theme to the entire application.
    
    Args:
        app: The QApplication instance
    """
    app.setStyle('Fusion')  # Use Fusion style as base
    app.setStyleSheet(get_dialog_stylesheet())

# Convenience function for backward compatibility with existing code
def get_theme_stylesheet(theme_name: str = "modern") -> str:
    """
    Get stylesheet for a named theme.
    Currently only supports 'modern' theme.
    
    Args:
        theme_name: Name of the theme (currently only 'modern')
    
    Returns:
        Complete stylesheet string
    """
    if theme_name.lower() == "modern":
        return get_dialog_stylesheet()
    else:
        # Fallback to modern theme for any unknown theme name
        return get_dialog_stylesheet()

# Export all public items
__all__ = [
    'MODERN_COLORS',
    'TYPOGRAPHY', 
    'SPACING',
    'get_button_style',
    'get_dialog_stylesheet',
    'apply_modern_style',
    'style_button',
    'apply_compact_layout',
    'create_styled_button',
    'apply_theme_to_application',
    'get_theme_stylesheet'
]