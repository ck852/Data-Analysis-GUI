"""
Simple peak detection and boundary adjustment for analysis ranges.

This module provides functionality to automatically adjust analysis range
boundaries to align with signal peaks within a small tolerance window.

Author: Data Analysis GUI Contributors
License: MIT
"""

import numpy as np
from typing import Tuple, Optional
from data_analysis_gui.core.dataset import ElectrophysiologyDataset
from data_analysis_gui.core.params import AnalysisParameters
from data_analysis_gui.config.logging import get_logger

logger = get_logger(__name__)


class PeakSnapper:
    """
    Adjusts analysis range boundaries to snap to nearby peaks.
    Uses simple derivative-based peak detection for maximum absolute value.
    """
    
    TOLERANCE_MS = 0.2  # Search window ±0.2 ms from specified boundary
    
    @staticmethod
    def find_peak_in_window(
        time_ms: np.ndarray,
        data: np.ndarray,
        target_time: float,
        tolerance: float = TOLERANCE_MS
    ) -> Optional[float]:
        """
        Find the peak with maximum absolute value within a time window.
        
        Args:
            time_ms: Time array in milliseconds
            data: Data array (voltage or current)
            target_time: Target time to search around (ms)
            tolerance: Search window ±tolerance from target (ms)
            
        Returns:
            Time position of peak if found, None otherwise
        """
        # Define search window
        window_start = target_time - tolerance
        window_end = target_time + tolerance
        
        # Find indices within window
        mask = (time_ms >= window_start) & (time_ms <= window_end)
        indices = np.where(mask)[0]
        
        if len(indices) < 3:  # Need at least 3 points for peak detection
            return None
        
        # Extract window data
        window_time = time_ms[indices]
        window_data = data[indices]
        
        # Find all local extrema using simple derivative method
        peaks = []
        for i in range(1, len(window_data) - 1):
            # Calculate discrete derivatives
            slope_before = (window_data[i] - window_data[i-1]) / (window_time[i] - window_time[i-1])
            slope_after = (window_data[i+1] - window_data[i]) / (window_time[i+1] - window_time[i])
            
            # Check for maximum
            if slope_before > 0 and slope_after < 0:
                peaks.append((window_time[i], abs(window_data[i])))
            # Check for minimum
            elif slope_before < 0 and slope_after > 0:
                peaks.append((window_time[i], abs(window_data[i])))
        
        if not peaks:
            return None
        
        # Return time of peak with maximum absolute value
        best_peak = max(peaks, key=lambda x: x[1])
        return best_peak[0]
    
    @staticmethod
    def adjust_boundaries(
        dataset: ElectrophysiologyDataset,
        params: AnalysisParameters,
        channel_definitions
    ) -> Tuple[AnalysisParameters, dict]:
        """
        Adjust analysis boundaries to snap to peaks if enabled.
        
        Args:
            dataset: The dataset to analyze
            params: Original analysis parameters
            channel_definitions: Channel configuration
            
        Returns:
            Tuple of (adjusted_parameters, adjustment_info_dict)
        """
        # Check if any snapping is enabled
        if not any([
            params.snap_range1_start,
            params.snap_range1_end,
            params.snap_range2_start,
            params.snap_range2_end
        ]):
            return params, {}
        
        # Get first sweep as representative (assuming peaks are consistent within file)
        sweep_indices = list(dataset.sweeps())
        if not sweep_indices:
            return params, {}
        
        first_sweep = sweep_indices[0]
        
        # Determine which channel to use for peak detection based on analysis type
        if params.y_axis.channel == "Current":
            channel_id = channel_definitions.get_current_channel()
        else:
            channel_id = channel_definitions.get_voltage_channel()
        
        # Get data for first sweep
        time_ms, channel_data = dataset.get_channel_vector(first_sweep, channel_id)
        
        if time_ms is None or channel_data is None:
            logger.warning("Could not extract data for peak snapping")
            return params, {}
        
        # Track adjustments
        adjustments = {}
        new_values = {}
        
        # Adjust Range 1 boundaries
        if params.snap_range1_start:
            new_start = PeakSnapper.find_peak_in_window(
                time_ms, channel_data, params.range1_start
            )
            if new_start is not None:
                adjustments['range1_start_adjusted'] = new_start
                new_values['range1_start'] = new_start
            else:
                new_values['range1_start'] = params.range1_start
        else:
            new_values['range1_start'] = params.range1_start
        
        if params.snap_range1_end:
            new_end = PeakSnapper.find_peak_in_window(
                time_ms, channel_data, params.range1_end
            )
            if new_end is not None:
                adjustments['range1_end_adjusted'] = new_end
                new_values['range1_end'] = new_end
            else:
                new_values['range1_end'] = params.range1_end
        else:
            new_values['range1_end'] = params.range1_end
        
        # Adjust Range 2 boundaries if dual range is enabled
        if params.use_dual_range:
            if params.snap_range2_start:
                new_start = PeakSnapper.find_peak_in_window(
                    time_ms, channel_data, params.range2_start
                )
                if new_start is not None:
                    adjustments['range2_start_adjusted'] = new_start
                    new_values['range2_start'] = new_start
                else:
                    new_values['range2_start'] = params.range2_start
            else:
                new_values['range2_start'] = params.range2_start
            
            if params.snap_range2_end:
                new_end = PeakSnapper.find_peak_in_window(
                    time_ms, channel_data, params.range2_end
                )
                if new_end is not None:
                    adjustments['range2_end_adjusted'] = new_end
                    new_values['range2_end'] = new_end
                else:
                    new_values['range2_end'] = params.range2_end
            else:
                new_values['range2_end'] = params.range2_end
        
        # Create new parameters with adjusted values
        if adjustments:
            adjusted_params = params.with_updates(**new_values)
            logger.debug(f"Boundaries adjusted: {adjustments}")
        else:
            adjusted_params = params
        
        return adjusted_params, adjustments