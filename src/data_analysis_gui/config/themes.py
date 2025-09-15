# config/themes.py
"""
Modern theme system for the Data Analysis GUI.
Provides consistent styling across all windows and dialogs.
All styling logic is centralized here for easy maintenance.
"""

from typing import Dict, Any, Optional
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QListWidget, 
                            QTableWidget, QProgressBar, QLabel, QCheckBox,
                            QGroupBox, QComboBox, QSpinBox, QDoubleSpinBox,
                            QLineEdit, QDialog, QMainWindow, QScrollArea,
                            QSplitter, QFrame, QHeaderView, QToolBar,
                            QStatusBar, QMenuBar, QMenu, QTableWidgetItem)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

# ============================================================================
# COLOR PALETTE
# ============================================================================

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
    'danger_pressed': '#BD2130',
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
    'alternating_row': '#FAFAFA',
    
    # Special elements
    'progress_bg': '#E9ECEF',
    'progress_chunk': '#0084FF',
    'separator': '#E0E0E0',
    
    # Status colors
    'info': '#6C91BF',
    'success': '#73AB84',
    
    # Invalid/error states
    'invalid_bg': '#ffcccc',
    'valid_bg': '#ccffcc',
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

TYPOGRAPHY = {
    'font_family': 'Segoe UI, -apple-system, BlinkMacSystemFont, Arial, sans-serif',
    'font_size_base': '18px',      # Increased from 10px
    'font_size_small': '17px',     # Increased from 9px
    'font_size_large': '20px',     # Increased from 12px
    'font_size_xlarge': '22px',    # Increased from 14px
    'font_weight_normal': '400',
    'font_weight_medium': '500',
    'font_weight_bold': '600',
    'line_height': '1.5',
    # Plot-specific sizes for matplotlib integration
    'plot_tick_size': 10,          # For matplotlib tick labels
    'plot_label_size': 11,         # For matplotlib axis labels
    'plot_title_size': 12,         # For matplotlib titles
    'plot_legend_size': 10,        # For matplotlib legends
}

# ============================================================================
# SPACING AND SIZING
# ============================================================================

SPACING = {
    'padding_xs': '2px',
    'padding_sm': '4px',
    'padding_md': '6px',       # Reduced from 8px for tighter layout
    'padding_lg': '10px',      # Reduced from 12px
    'padding_xl': '14px',      # Reduced from 16px
    'margin_xs': '2px',
    'margin_sm': '4px',
    'margin_md': '6px',        # Reduced from 8px
    'margin_lg': '10px',       # Reduced from 12px
    'margin_xl': '14px',       # Reduced from 16px
    'border_radius': '3px',
    'border_radius_lg': '4px',
    'border_radius_xl': '6px',
}

WIDGET_SIZES = {
    'button_height': 30,           # Increased from 28 to accommodate larger font
    'button_min_width': 80,
    'input_height': 30,            # Increased from 28 to match button height
    'checkbox_size': 16,
    'color_indicator_size': 20,
    'min_dialog_width': 900,
    'min_dialog_height': 650,
    'toolbar_icon_size': 16,
    'list_item_height': 26,        # Increased from 24
    'group_box_margin_top': 6,     # Reduced from 8
}

# ============================================================================
# BUTTON STYLES
# ============================================================================

def get_button_style(style_type: str = "secondary") -> str:
    """Get button stylesheet for different button types."""
    styles = {
        "primary": {
            'bg': MODERN_COLORS['primary'],
            'hover': MODERN_COLORS['primary_hover'],
            'pressed': MODERN_COLORS['primary_pressed'],
            'text': 'white'
        },
        "accent": {
            'bg': MODERN_COLORS['accent'],
            'hover': MODERN_COLORS['accent_hover'],
            'pressed': MODERN_COLORS['accent_pressed'],
            'text': 'white'
        },
        "danger": {
            'bg': MODERN_COLORS['danger'],
            'hover': MODERN_COLORS['danger_hover'],
            'pressed': MODERN_COLORS['danger_pressed'],
            'text': 'white'
        },
        "warning": {
            'bg': MODERN_COLORS['warning'],
            'hover': MODERN_COLORS['warning_hover'],
            'pressed': '#E09800',
            'text': '#212529'
        },
        "secondary": {
            'bg': MODERN_COLORS['secondary'],
            'hover': MODERN_COLORS['secondary_hover'],
            'pressed': MODERN_COLORS['secondary_pressed'],
            'text': MODERN_COLORS['secondary_text'],
            'border': f"1px solid {MODERN_COLORS['secondary_border']}"
        }
    }
    
    style = styles.get(style_type, styles['secondary'])
    border = style.get('border', 'none')
    
    return f"""
        QPushButton {{
            background-color: {style['bg']};
            color: {style['text']};
            border: {border};
            border-radius: {SPACING['border_radius']};
            padding: 6px 16px;
            font-size: {TYPOGRAPHY['font_size_base']};
            font-weight: {TYPOGRAPHY['font_weight_medium']};
            font-family: {TYPOGRAPHY['font_family']};
            min-height: {WIDGET_SIZES['button_height']}px;
            min-width: {WIDGET_SIZES['button_min_width']}px;
        }}
        QPushButton:hover {{
            background-color: {style['hover']};
            {f"border-color: {MODERN_COLORS['secondary_hover_border']};" if 'border' in style else ""}
        }}
        QPushButton:pressed {{
            background-color: {style['pressed']};
        }}
        QPushButton:disabled {{
            background-color: {MODERN_COLORS['disabled_bg']};
            color: {MODERN_COLORS['disabled_text']};
            border-color: {MODERN_COLORS['border']};
        }}
    """

def create_styled_button(text: str, style_type: str = "secondary", 
                        parent: QWidget = None) -> QPushButton:
    """Create a new button with modern styling."""
    button = QPushButton(text, parent)
    style_button(button, style_type)
    return button

def style_button(button: QPushButton, style_type: str = "secondary") -> None:
    """Apply modern styling to a specific button."""
    button.setStyleSheet(get_button_style(style_type))

# ============================================================================
# LIST AND TABLE WIDGETS
# ============================================================================

def style_list_widget(widget: QListWidget) -> None:
    """Apply standard styling to a QListWidget."""
    widget.setStyleSheet(f"""
        QListWidget {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            background-color: {MODERN_COLORS['background']};
            padding: {SPACING['padding_xs']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        QListWidget::item {{
            padding: {SPACING['padding_sm']};
            min-height: {WIDGET_SIZES['list_item_height']}px;
            border-bottom: 1px solid {MODERN_COLORS['list_border']};
        }}
        QListWidget::item:selected {{
            background-color: {MODERN_COLORS['list_selected']};
            color: {MODERN_COLORS['list_selected_text']};
        }}
        QListWidget::item:hover {{
            background-color: {MODERN_COLORS['list_hover']};
        }}
    """)

def style_table_widget(widget: QTableWidget) -> None:
    """Apply standard styling to a QTableWidget."""
    widget.setAlternatingRowColors(True)
    widget.setStyleSheet(f"""
        QTableWidget {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            background-color: {MODERN_COLORS['background']};
            alternate-background-color: {MODERN_COLORS['alternating_row']};
            gridline-color: {MODERN_COLORS['list_border']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        QTableWidget::item {{
            padding: {SPACING['padding_sm']};
            border: none;
        }}
        QTableWidget::item:selected {{
            background-color: {MODERN_COLORS['list_selected']};
            color: {MODERN_COLORS['list_selected_text']};
        }}
        QTableWidget::item:hover {{
            background-color: {MODERN_COLORS['list_hover']};
        }}
        QHeaderView::section {{
            background-color: {MODERN_COLORS['surface']};
            border: none;
            border-bottom: 2px solid {MODERN_COLORS['border']};
            border-right: 1px solid {MODERN_COLORS['border']};
            padding: {SPACING['padding_sm']} {SPACING['padding_md']};
            font-weight: {TYPOGRAPHY['font_weight_medium']};
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        QTableWidget QTableCornerButton::section {{
            background-color: {MODERN_COLORS['surface']};
            border: none;
            border-bottom: 2px solid {MODERN_COLORS['border']};
            border-right: 1px solid {MODERN_COLORS['border']};
        }}
    """)

# ============================================================================
# PROGRESS BARS
# ============================================================================

def style_progress_bar(widget: QProgressBar) -> None:
    """Apply standard styling to a QProgressBar."""
    widget.setStyleSheet(f"""
        QProgressBar {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            text-align: center;
            font-size: {TYPOGRAPHY['font_size_small']};
            font-family: {TYPOGRAPHY['font_family']};
            background-color: {MODERN_COLORS['progress_bg']};
            min-height: 20px;
            max-height: 20px;
        }}
        QProgressBar::chunk {{
            background-color: {MODERN_COLORS['progress_chunk']};
            border-radius: 2px;
        }}
    """)

# ============================================================================
# GROUPS AND CONTAINERS
# ============================================================================

def style_group_box(widget: QGroupBox) -> None:
    """Apply standard styling to a QGroupBox with tighter spacing."""
    widget.setStyleSheet(f"""
        QGroupBox {{
            font-weight: {TYPOGRAPHY['font_weight_medium']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius_lg']};
            margin-top: {WIDGET_SIZES['group_box_margin_top']}px;
            padding-top: {SPACING['padding_md']};
            padding-bottom: {SPACING['padding_xs']};
            padding-left: {SPACING['padding_sm']};
            padding-right: {SPACING['padding_sm']};
        }}
        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: {SPACING['padding_md']};
            padding: 0 {SPACING['padding_sm']};
            color: {MODERN_COLORS['text']};
            background-color: {MODERN_COLORS['background']};
        }}
    """)

def style_scroll_area(widget: QScrollArea) -> None:
    """Apply standard styling to a QScrollArea."""
    widget.setStyleSheet(f"""
        QScrollArea {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            background-color: {MODERN_COLORS['background']};
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
    """)

def style_splitter(widget: QSplitter) -> None:
    """Apply standard styling to a QSplitter."""
    widget.setStyleSheet(f"""
        QSplitter::handle {{
            background: {MODERN_COLORS['border']};
            width: 2px;
            height: 2px;
        }}
        QSplitter::handle:hover {{
            background: {MODERN_COLORS['secondary_hover_border']};
        }}
        QSplitter::handle:pressed {{
            background: {MODERN_COLORS['primary']};
        }}
    """)

# ============================================================================
# INPUT WIDGETS
# ============================================================================

def style_checkbox(widget: QCheckBox) -> None:
    """Apply standard styling to a QCheckBox."""
    widget.setStyleSheet(f"""
        QCheckBox {{
            spacing: {SPACING['padding_sm']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
            color: {MODERN_COLORS['text']};
        }}
        QCheckBox::indicator {{
            width: {WIDGET_SIZES['checkbox_size']}px;
            height: {WIDGET_SIZES['checkbox_size']}px;
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: 3px;
            background-color: {MODERN_COLORS['background']};
        }}
        QCheckBox::indicator:checked {{
            background-color: {MODERN_COLORS['primary']};
            border-color: {MODERN_COLORS['primary']};
            image: url(checkmark.png);  /* Optional: add checkmark image */
        }}
        QCheckBox::indicator:hover {{
            border-color: {MODERN_COLORS['primary_hover']};
        }}
        QCheckBox::indicator:disabled {{
            background-color: {MODERN_COLORS['disabled_bg']};
            border-color: {MODERN_COLORS['border']};
        }}
    """)

def style_input_field(widget: QWidget) -> None:
    """Apply standard styling to input fields (QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox)."""
    widget.setStyleSheet(f"""
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: 4px 8px;
            background-color: {MODERN_COLORS['background']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
            min-height: {WIDGET_SIZES['input_height']}px;
            color: {MODERN_COLORS['text']};
        }}
        QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {MODERN_COLORS['secondary_hover_border']};
        }}
        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {MODERN_COLORS['border_focus']};
            outline: none;
        }}
        QLineEdit:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{
            background-color: {MODERN_COLORS['disabled_bg']};
            color: {MODERN_COLORS['disabled_text']};
            border-color: {MODERN_COLORS['border']};
        }}
        QSpinBox::up-button, QDoubleSpinBox::up-button {{
            border: none;
            background: {MODERN_COLORS['surface']};
        }}
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            border: none;
            background: {MODERN_COLORS['surface']};
        }}
        QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover,
        QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
            background: {MODERN_COLORS['secondary_hover']};
        }}
    """)

def style_combo_box(widget: QComboBox) -> None:
    """Apply standard styling to a QComboBox."""
    widget.setStyleSheet(f"""
        QComboBox {{
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: 4px 8px;
            background-color: {MODERN_COLORS['background']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
            min-height: {WIDGET_SIZES['input_height']}px;
            color: {MODERN_COLORS['text']};
        }}
        QComboBox:hover {{
            border-color: {MODERN_COLORS['secondary_hover_border']};
        }}
        QComboBox:focus {{
            border-color: {MODERN_COLORS['border_focus']};
        }}
        QComboBox:disabled {{
            background-color: {MODERN_COLORS['disabled_bg']};
            color: {MODERN_COLORS['disabled_text']};
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
        QComboBox QAbstractItemView {{
            border: 1px solid {MODERN_COLORS['border']};
            background-color: {MODERN_COLORS['background']};
            selection-background-color: {MODERN_COLORS['list_selected']};
            selection-color: {MODERN_COLORS['list_selected_text']};
        }}
    """)

def style_input_invalid(widget: QWidget) -> None:
    """Apply invalid state styling to an input widget."""
    widget.setStyleSheet(widget.styleSheet() + f"""
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {MODERN_COLORS['invalid_bg']};
            border-color: {MODERN_COLORS['danger']};
        }}
    """)

def style_input_valid(widget: QWidget) -> None:
    """Apply valid state styling to an input widget."""
    widget.setStyleSheet(widget.styleSheet() + f"""
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {MODERN_COLORS['valid_bg']};
            border-color: {MODERN_COLORS['success']};
        }}
    """)

# ============================================================================
# LABELS AND TEXT
# ============================================================================

def style_label(widget: QLabel, style_type: str = "normal") -> None:
    """Apply standard styling to a QLabel."""
    styles = {
        'normal': {
            'color': MODERN_COLORS['text'],
            'size': TYPOGRAPHY['font_size_base'],
            'weight': TYPOGRAPHY['font_weight_normal']
        },
        'heading': {
            'color': MODERN_COLORS['text'],
            'size': TYPOGRAPHY['font_size_xlarge'],
            'weight': TYPOGRAPHY['font_weight_bold']
        },
        'subheading': {
            'color': MODERN_COLORS['text'],
            'size': TYPOGRAPHY['font_size_large'],
            'weight': TYPOGRAPHY['font_weight_medium']
        },
        'muted': {
            'color': MODERN_COLORS['text_muted'],
            'size': TYPOGRAPHY['font_size_small'],
            'weight': TYPOGRAPHY['font_weight_normal']
        },
        'caption': {
            'color': MODERN_COLORS['text_muted'],
            'size': TYPOGRAPHY['font_size_small'],
            'weight': TYPOGRAPHY['font_weight_normal'],
            'style': 'italic'
        }
    }
    
    style = styles.get(style_type, styles['normal'])
    style_str = f"""
        QLabel {{
            color: {style['color']};
            font-size: {style['size']};
            font-weight: {style['weight']};
            font-family: {TYPOGRAPHY['font_family']};
            {f"font-style: {style.get('style', 'normal')};" if 'style' in style else ""}
        }}
    """
    widget.setStyleSheet(style_str)

def style_status_label(widget: QLabel, status_type: str = "normal") -> None:
    """Apply status-specific styling to a QLabel."""
    color_map = {
        'normal': MODERN_COLORS['text'],
        'info': MODERN_COLORS['info'],
        'success': MODERN_COLORS['success'],
        'warning': MODERN_COLORS['warning'],
        'error': MODERN_COLORS['danger'],
        'muted': MODERN_COLORS['text_muted']
    }
    
    color = color_map.get(status_type, MODERN_COLORS['text'])
    weight = TYPOGRAPHY['font_weight_medium'] if status_type != 'normal' else TYPOGRAPHY['font_weight_normal']
    
    widget.setStyleSheet(f"""
        QLabel {{
            color: {color};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-weight: {weight};
            font-family: {TYPOGRAPHY['font_family']};
            padding: {SPACING['padding_xs']} 0;
        }}
    """)

# ============================================================================
# TOOLBARS AND MENUS
# ============================================================================

def style_toolbar(widget: QToolBar) -> None:
    """Apply standard styling to a QToolBar."""
    widget.setStyleSheet(f"""
        QToolBar {{
            background-color: {MODERN_COLORS['surface']};
            border-bottom: 1px solid {MODERN_COLORS['border']};
            padding: {SPACING['padding_xs']};
            spacing: {SPACING['margin_xs']};
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
    """)

def style_menu_bar(widget: QMenuBar) -> None:
    """Apply standard styling to a QMenuBar."""
    widget.setStyleSheet(f"""
        QMenuBar {{
            background-color: {MODERN_COLORS['surface']};
            border-bottom: 1px solid {MODERN_COLORS['border']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        QMenuBar::item {{
            padding: 4px 10px;
            background: transparent;
        }}
        QMenuBar::item:selected {{
            background-color: {MODERN_COLORS['secondary_hover']};
        }}
        QMenuBar::item:pressed {{
            background-color: {MODERN_COLORS['secondary_pressed']};
        }}
    """)

def style_menu(widget: QMenu) -> None:
    """Apply standard styling to a QMenu."""
    widget.setStyleSheet(f"""
        QMenu {{
            background-color: {MODERN_COLORS['background']};
            border: 1px solid {MODERN_COLORS['border']};
            border-radius: {SPACING['border_radius']};
            padding: {SPACING['padding_xs']};
            font-size: {TYPOGRAPHY['font_size_base']};
            font-family: {TYPOGRAPHY['font_family']};
        }}
        QMenu::item {{
            padding: 6px 20px;
            border-radius: {SPACING['border_radius']};
        }}
        QMenu::item:selected {{
            background-color: {MODERN_COLORS['list_selected']};
            color: {MODERN_COLORS['list_selected_text']};
        }}
        QMenu::separator {{
            height: 1px;
            background: {MODERN_COLORS['separator']};
            margin: 4px 10px;
        }}
        QMenu::indicator {{
            width: 13px;
            height: 13px;
        }}
    """)

def style_status_bar(widget: QStatusBar) -> None:
    """Apply standard styling to a QStatusBar."""
    widget.setStyleSheet(f"""
        QStatusBar {{
            background-color: {MODERN_COLORS['surface']};
            border-top: 1px solid {MODERN_COLORS['border']};
            font-size: {TYPOGRAPHY['font_size_small']};
            font-family: {TYPOGRAPHY['font_family']};
            color: {MODERN_COLORS['text_muted']};
            padding: {SPACING['padding_xs']};
        }}
        QStatusBar::item {{
            border: none;
        }}
    """)

# ============================================================================
# DIALOGS AND WINDOWS
# ============================================================================

def get_dialog_stylesheet() -> str:
    """Get the complete stylesheet for dialogs and windows."""
    return f"""
        QDialog, QMainWindow {{
            background-color: {MODERN_COLORS['background']};
            font-family: {TYPOGRAPHY['font_family']};
            font-size: {TYPOGRAPHY['font_size_base']};
        }}
        
        QWidget {{
            font-family: {TYPOGRAPHY['font_family']};
        }}
        
        QFrame {{
            border: none;
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
    """Apply modern styling to a widget and all its children."""
    widget.setStyleSheet(get_dialog_stylesheet())

def apply_compact_layout(widget: QWidget, spacing: int = 6, margin: int = 10) -> None:
    """Apply compact spacing to a widget's layout. Reduced defaults for tighter UI."""
    if widget.layout():
        widget.layout().setSpacing(spacing)
        widget.layout().setContentsMargins(margin, margin, margin, margin)

def style_dialog(dialog: QDialog, title: str = None) -> None:
    """Apply complete styling to a dialog."""
    apply_modern_style(dialog)
    if title:
        dialog.setWindowTitle(title)
    dialog.setMinimumWidth(WIDGET_SIZES['min_dialog_width'])
    dialog.setMinimumHeight(WIDGET_SIZES['min_dialog_height'])

def style_main_window(window: QMainWindow) -> None:
    """Apply complete styling to a main window."""
    apply_modern_style(window)
    if window.menuBar():
        style_menu_bar(window.menuBar())
    if window.statusBar():
        style_status_bar(window.statusBar())
    # Style all toolbars
    for toolbar in window.findChildren(QToolBar):
        style_toolbar(toolbar)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_file_count_color(count: int, max_count: int = 10) -> str:
    """Get appropriate color for file count display."""
    if count == 0:
        return MODERN_COLORS['text_muted']
    elif count < max_count // 2:
        return MODERN_COLORS['info']
    else:
        return MODERN_COLORS['success']

def get_status_color(status: str) -> str:
    """Get appropriate color for status display."""
    status_map = {
        'success': MODERN_COLORS['success'],
        'warning': MODERN_COLORS['warning'],
        'error': MODERN_COLORS['danger'],
        'info': MODERN_COLORS['info'],
        'processing': MODERN_COLORS['primary'],
        'muted': MODERN_COLORS['text_muted']
    }
    return status_map.get(status.lower(), MODERN_COLORS['text'])

def get_selection_summary_color(selected: int, total: int) -> str:
    """Get color for selection summary based on ratio."""
    if selected == 0:
        return MODERN_COLORS['warning']
    elif selected == total:
        return MODERN_COLORS['success']
    else:
        return MODERN_COLORS['info']

def apply_theme_to_application(app: QApplication) -> None:
    """Apply the modern theme to the entire application."""
    app.setStyle('Fusion')  # Use Fusion style as base
    
    # Set application palette for consistent colors
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(MODERN_COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(MODERN_COLORS['text']))
    palette.setColor(QPalette.Base, QColor(MODERN_COLORS['background']))
    palette.setColor(QPalette.AlternateBase, QColor(MODERN_COLORS['alternating_row']))
    palette.setColor(QPalette.ToolTipBase, QColor(MODERN_COLORS['surface']))
    palette.setColor(QPalette.ToolTipText, QColor(MODERN_COLORS['text']))
    palette.setColor(QPalette.Text, QColor(MODERN_COLORS['text']))
    palette.setColor(QPalette.Button, QColor(MODERN_COLORS['secondary']))
    palette.setColor(QPalette.ButtonText, QColor(MODERN_COLORS['text']))
    palette.setColor(QPalette.BrightText, Qt.white)
    palette.setColor(QPalette.Link, QColor(MODERN_COLORS['primary']))
    palette.setColor(QPalette.Highlight, QColor(MODERN_COLORS['list_selected']))
    palette.setColor(QPalette.HighlightedText, QColor(MODERN_COLORS['list_selected_text']))
    app.setPalette(palette)
    
    app.setStyleSheet(get_dialog_stylesheet())

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def apply_widget_palette(widget: QWidget, style_name: str = "default") -> None:
    """Apply a complete style palette to a widget and its children."""
    # Style the widget based on its type
    if isinstance(widget, QListWidget):
        style_list_widget(widget)
    elif isinstance(widget, QTableWidget):
        style_table_widget(widget)
    elif isinstance(widget, QProgressBar):
        style_progress_bar(widget)
    elif isinstance(widget, QGroupBox):
        style_group_box(widget)
    elif isinstance(widget, QCheckBox):
        style_checkbox(widget)
    elif isinstance(widget, QComboBox):
        style_combo_box(widget)
    elif isinstance(widget, (QLineEdit, QSpinBox, QDoubleSpinBox)):
        style_input_field(widget)
    elif isinstance(widget, QScrollArea):
        style_scroll_area(widget)
    elif isinstance(widget, QSplitter):
        style_splitter(widget)
    
    # Recursively style children
    for child in widget.findChildren(QWidget):
        apply_widget_palette(child, style_name)

# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

def get_theme_stylesheet(theme_name: str = "modern") -> str:
    """Get stylesheet for a named theme (backward compatibility)."""
    return get_dialog_stylesheet()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Color constants
    'MODERN_COLORS',
    'TYPOGRAPHY', 
    'SPACING',
    'WIDGET_SIZES',
    
    # Button functions
    'get_button_style',
    'create_styled_button',
    'style_button',
    
    # Widget styling functions
    'style_list_widget',
    'style_table_widget',
    'style_progress_bar',
    'style_group_box',
    'style_checkbox',
    'style_input_field',
    'style_combo_box',
    'style_input_invalid',
    'style_input_valid',
    'style_scroll_area',
    'style_splitter',
    
    # Label functions
    'style_label',
    'style_status_label',
    
    # Navigation functions
    'style_toolbar',
    'style_menu_bar',
    'style_menu',
    'style_status_bar',
    
    # Dialog/Window functions
    'get_dialog_stylesheet',
    'apply_modern_style',
    'apply_compact_layout',
    'style_dialog',
    'style_main_window',
    
    # Utility functions
    'get_file_count_color',
    'get_status_color',
    'get_selection_summary_color',
    'apply_theme_to_application',
    'apply_widget_palette',
    
    # Backward compatibility
    'get_theme_stylesheet',
]