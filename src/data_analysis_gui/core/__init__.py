"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

# src/data_analysis_gui/core/__init__.py
"""
Core business logic module for the data analysis GUI.
"""

from .channel_definitions import ChannelDefinitions


__all__ = ["ChannelDefinitions", "CurrentDensityExporter"]
