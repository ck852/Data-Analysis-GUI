"""
Session settings persistence for analysis parameters.
Simplified version with direct state application - no pending states.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt5.QtCore import QStandardPaths
from PyQt5.QtWidgets import QSplitter


SETTINGS_VERSION = "1.0"


def get_settings_dir() -> Path:
    """Get the application settings directory, creating if needed."""
    app_config = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    settings_dir = Path(app_config) / "data_analysis_gui"
    settings_dir.mkdir(parents=True, exist_ok=True)
    return settings_dir


def save_session_settings(settings: Dict[str, Any]) -> bool:
    """
    Save session settings with version info.
    
    Args:
        settings: Complete settings dictionary
        
    Returns:
        True if saved successfully
    """
    try:
        settings_file = get_settings_dir() / "session_settings.json"
        
        # Add version for future compatibility
        settings_with_version = {
            "version": SETTINGS_VERSION,
            "settings": settings
        }
        
        with open(settings_file, 'w') as f:
            json.dump(settings_with_version, f, indent=2)
        return True
    except Exception as e:
        print(f"Failed to save session settings: {e}")
        return False


def load_session_settings() -> Optional[Dict[str, Any]]:
    """
    Load session settings, handling version compatibility.
    
    Returns:
        Settings dictionary if valid, None otherwise
    """
    try:
        settings_file = get_settings_dir() / "session_settings.json"
        if not settings_file.exists():
            return None
            
        with open(settings_file, 'r') as f:
            data = json.load(f)
        
        # Handle both old format (direct dict) and new format (with version)
        if isinstance(data, dict):
            if "version" in data and "settings" in data:
                # New format
                return data["settings"]
            else:
                # Old format - treat as settings directly
                return data
                
    except Exception as e:
        print(f"Failed to load session settings: {e}")
    return None


def extract_settings_from_main_window(main_window) -> Dict[str, Any]:
    """
    Extract all relevant settings from the main window.
    
    Args:
        main_window: The MainWindow instance
        
    Returns:
        Dictionary of all settings
    """
    settings = {}
    
    # Get control panel parameters
    if hasattr(main_window, 'control_panel'):
        params = main_window.control_panel.get_parameters()
        
        # Analysis settings
        settings['analysis'] = {
            'range1_start': params.range1_start,
            'range1_end': params.range1_end,
            'use_dual_range': params.use_dual_range,
            'range2_start': params.range2_start,
            'range2_end': params.range2_end,
            'stimulus_period': params.stimulus_period,
        }
        
        # Plot settings
        settings['plot'] = {
            'x_measure': params.x_axis.measure,
            'x_channel': params.x_axis.channel,
            'y_measure': params.y_axis.measure,
            'y_channel': params.y_axis.channel,
            'peak_mode': params.x_axis.peak_type or params.y_axis.peak_type or 'Absolute'
        }
    
    # Channel configuration - always save current toggle state
    if hasattr(main_window, 'channel_toggle'):
        settings['channel'] = {
            'is_swapped': main_window.channel_toggle.is_swapped
        }
    
    # Current view settings (if a file is loaded)
    if main_window.current_file_path:
        settings['view'] = {
            'last_directory': str(Path(main_window.current_file_path).parent),
            'channel_view': main_window.channel_combo.currentText() if hasattr(main_window, 'channel_combo') else 'Voltage'
        }
    
    # Window geometry
    settings['window'] = {
        'geometry': {
            'x': main_window.x(),
            'y': main_window.y(),
            'width': main_window.width(),
            'height': main_window.height()
        },
        'maximized': main_window.isMaximized()
    }
    
    # Splitter position
    if hasattr(main_window, 'splitter'):
        splitter = main_window.findChild(QSplitter)
        if splitter:
            settings['window']['splitter_sizes'] = splitter.sizes()
    
    return settings


def apply_settings_to_main_window(main_window, settings: Dict[str, Any]):
    """
    Apply settings to the main window.
    Simplified version - all settings are applied directly without pending states.
    
    Args:
        main_window: The MainWindow instance
        settings: Settings dictionary
    """
    if not settings:
        return
    
    # Window geometry - always applied first
    if 'window' in settings:
        window_settings = settings['window']
        
        # Apply geometry if not maximized
        if not window_settings.get('maximized', False):
            if 'geometry' in window_settings:
                geo = window_settings['geometry']
                main_window.setGeometry(geo['x'], geo['y'], geo['width'], geo['height'])
        else:
            main_window.showMaximized()
        
        # Apply splitter sizes
        if 'splitter_sizes' in window_settings:
            from PyQt5.QtWidgets import QSplitter
            splitter = main_window.findChild(QSplitter)
            if splitter:
                splitter.setSizes(window_settings['splitter_sizes'])
    
    # Apply analysis settings to control panel immediately
    if 'analysis' in settings and hasattr(main_window, 'control_panel'):
        main_window.control_panel.set_parameters_from_dict(settings['analysis'])
    
    # Apply plot settings immediately
    if 'plot' in settings and hasattr(main_window, 'control_panel'):
        main_window.control_panel.set_plot_settings_from_dict(settings['plot'])
    
    # Apply channel swap state directly
    if 'channel' in settings and hasattr(main_window, 'channel_toggle'):
        is_swapped = settings['channel'].get('is_swapped', False)
        # Set the toggle switch state
        main_window.channel_toggle.set_swapped(is_swapped)
        # Set the control panel state
        if hasattr(main_window, 'control_panel'):
            main_window.control_panel.set_swap_state(is_swapped)
        # Also update the controller's channel definitions if they exist
        if hasattr(main_window, 'channel_definitions'):
            try:
                # If the channel definitions support being set directly
                if is_swapped != main_window.channel_definitions.is_swapped():
                    main_window.controller.swap_channels()
            except:
                # If channel_definitions doesn't exist yet or doesn't support is_swapped,
                # that's fine - the state will be synced when a file is loaded
                pass
    
    # Store view settings for later use (when file is loaded)
    if 'view' in settings:
        main_window.last_channel_view = settings['view'].get('channel_view', 'Voltage')
        main_window.last_directory = settings['view'].get('last_directory')


def revalidate_ranges_for_file(main_window, max_sweep_time: float):
    """
    Revalidate and clamp range values after a file is loaded.
    
    Args:
        main_window: The MainWindow instance
        max_sweep_time: Maximum sweep time from the loaded file
    """
    if hasattr(main_window, 'control_panel'):
        control = main_window.control_panel
        
        # Update the max range for all spinboxes
        control.set_analysis_range(max_sweep_time)
        
        # The set_analysis_range method already clamps values,
        # and validation happens automatically


# Backward compatibility functions
def save_last_session(params: dict) -> None:
    """Legacy function for compatibility."""
    save_session_settings(params)


def load_last_session() -> dict:
    """Legacy function for compatibility."""
    return load_session_settings()