"""
Formats analysis data for plots and exports.
PHASE 5: Pure transformation logic with no side effects.
FIXED: Corrected dual range export when X-axis is Time
"""

from typing import Dict, List, Any, Tuple, Optional
import numpy as np

from data_analysis_gui.core.metrics_calculator import SweepMetrics
from data_analysis_gui.core.params import AnalysisParameters, AxisConfig
from data_analysis_gui.config.logging import get_logger

logger = get_logger(__name__)


class PlotFormatter:
    """
    Pure data transformation for plot and export formatting.
    All methods are stateless transformations.
    """
    
    def format_for_plot(
        self,
        metrics: List[SweepMetrics],
        params: AnalysisParameters
    ) -> Dict[str, Any]:
        """Format metrics for plotting."""
        if not metrics:
            return self.empty_plot_data()
        
        # Log the parameters for debugging
        logger.debug(f"Formatting plot with X-axis: {params.x_axis.measure}, Y-axis: {params.y_axis.measure}")
        if params.x_axis.measure == "Peak":
            logger.debug(f"X-axis peak type: {params.x_axis.peak_type}")
        if params.y_axis.measure == "Peak":
            logger.debug(f"Y-axis peak type: {params.y_axis.peak_type}")
        
        # Extract data
        x_data, x_label = self._extract_axis_data(metrics, params.x_axis, 1)
        y_data, y_label = self._extract_axis_data(metrics, params.y_axis, 1)
        
        result = {
            'x_data': np.array(x_data),
            'y_data': np.array(y_data),
            'x_label': x_label,
            'y_label': y_label,
            'sweep_indices': [m.sweep_index for m in metrics]
        }
        
        if params.use_dual_range:
            # For dual range, x_data2 should only be different if X-axis measures
            # something that can vary between ranges (Voltage or Current)
            if params.x_axis.measure == "Time":
                # Time is the same for both ranges
                result['x_data2'] = result['x_data']  # Use same time data
            else:
                # Extract separate x-data for range 2 (voltage or current can differ)
                x_data2, _ = self._extract_axis_data(metrics, params.x_axis, 2)
                result['x_data2'] = np.array(x_data2)
            
            # Y-data is always extracted separately for range 2
            y_data2, _ = self._extract_axis_data(metrics, params.y_axis, 2)
            result['y_data2'] = np.array(y_data2)
            
            # Add voltage labels for Y-axis labels
            avg_v1 = np.nanmean([m.voltage_mean_r1 for m in metrics])
            avg_v2 = np.nanmean([m.voltage_mean_r2 for m in metrics 
                                if m.voltage_mean_r2 is not None])
            
            result['y_label_r1'] = self._format_range_label(y_label, avg_v1)
            result['y_label_r2'] = self._format_range_label(y_label, avg_v2)
        else:
            result['x_data2'] = np.array([])
            result['y_data2'] = np.array([])
        
        return result
    
    def format_for_export(
        self,
        plot_data: Dict[str, Any],
        params: AnalysisParameters
    ) -> Dict[str, Any]:
        """Format plot data for CSV export."""
        if len(plot_data.get('x_data', [])) == 0:
            return {'headers': [], 'data': np.array([[]]), 'format_spec': '%.6f'}
        
        if params.use_dual_range and len(plot_data.get('y_data2', [])) > 0:
            return self._format_dual_range_export(plot_data, params)
        else:
            return self._format_single_range_export(plot_data)
    
    def format_peak_analysis(
        self,
        metrics: List[SweepMetrics],
        params: AnalysisParameters,
        peak_types: List[str]
    ) -> Dict[str, Any]:
        """Format peak analysis data."""
        if not metrics:
            return {}
        
        # Extract x-axis data (common for all peak types)
        x_data, x_label = self._extract_axis_data(metrics, params.x_axis, 1)
        
        peak_data = {}
        
        for peak_type in peak_types:
            logger.debug(f"Processing peak analysis for type: {peak_type}")
            
            # Create modified y-axis config for this peak type
            y_axis_config = AxisConfig(
                measure="Peak",
                channel=params.y_axis.channel,
                peak_type=peak_type
            )
            
            # Extract data for both ranges if dual range is enabled
            y_data_r1, y_label_r1 = self._extract_axis_data(metrics, y_axis_config, 1)
            
            peak_data[peak_type] = {
                'data': np.array(y_data_r1),
                'label': y_label_r1
            }
            
            if params.use_dual_range:
                y_data_r2, y_label_r2 = self._extract_axis_data(metrics, y_axis_config, 2)
                peak_data[f"{peak_type}_Range2"] = {
                    'data': np.array(y_data_r2),
                    'label': f"{y_label_r2} (Range 2)"
                }
        
        return {
            'peak_data': peak_data,
            'x_data': np.array(x_data),
            'x_label': x_label,
            'sweep_indices': [m.sweep_index for m in metrics]
        }
    
    def empty_plot_data(self) -> Dict[str, Any]:
        """Create empty plot data structure."""
        return {
            'x_data': np.array([]),
            'y_data': np.array([]),
            'x_data2': np.array([]),
            'y_data2': np.array([]),
            'x_label': '',
            'y_label': '',
            'sweep_indices': []
        }
    
    def _extract_axis_data(
        self,
        metrics: List[SweepMetrics],
        axis_config: AxisConfig,
        range_num: int
    ) -> Tuple[List[float], str]:
        """
        Extract data for specific axis with proper peak mode handling.
        
        FIXED: Added validation and logging for peak type handling.
        """
        if axis_config.measure == "Time":
            return [m.time_s for m in metrics], "Time (s)"
        
        # Determine channel and unit
        channel_prefix = "voltage" if axis_config.channel == "Voltage" else "current"
        unit = "mV" if axis_config.channel == "Voltage" else "pA"
        
        if axis_config.measure == "Average":
            metric_name = f"{channel_prefix}_mean_r{range_num}"
            label = f"Average {axis_config.channel} ({unit})"
            logger.debug(f"Extracting average data from metric: {metric_name}")
            
        elif axis_config.measure == "Peak":
            # FIXED: Validate peak_type is set and valid
            if axis_config.peak_type is None:
                logger.warning(f"Peak type not specified for {axis_config.channel}, defaulting to Absolute")
                peak_type = "Absolute"
            else:
                peak_type = axis_config.peak_type
                logger.debug(f"Using peak type: {peak_type} for {axis_config.channel}")
            
            # Map user-friendly names to metric field names
            peak_map = {
                "Absolute": "absolute",
                "Positive": "positive",
                "Negative": "negative",
                "Peak-Peak": "peakpeak"
            }
            
            # FIXED: Validate peak_type is in our map
            if peak_type not in peak_map:
                logger.error(f"Invalid peak type: {peak_type}. Using Absolute as fallback.")
                peak_type = "Absolute"
            
            metric_base = peak_map[peak_type]
            metric_name = f"{channel_prefix}_{metric_base}_r{range_num}"
            
            # Create descriptive label
            peak_labels = {
                "Absolute": "Peak",
                "Positive": "Peak (+)",
                "Negative": "Peak (-)",
                "Peak-Peak": "Peak-Peak"
            }
            peak_label = peak_labels.get(peak_type, "Peak")
            label = f"{peak_label} {axis_config.channel} ({unit})"
            
            logger.debug(f"Extracting peak data from metric: {metric_name}")
        
        else:
            # Shouldn't happen with current UI, but handle gracefully
            logger.warning(f"Unknown measure type: {axis_config.measure}, defaulting to Average")
            metric_name = f"{channel_prefix}_mean_r{range_num}"
            label = f"{axis_config.measure} {axis_config.channel} ({unit})"
        
        # Extract data with error handling
        data = []
        missing_count = 0
        
        for i, m in enumerate(metrics):
            try:
                value = getattr(m, metric_name)
                if value is None:
                    logger.warning(f"None value in metric {metric_name} for sweep {m.sweep_index}")
                    value = np.nan
                data.append(value)
            except AttributeError:
                missing_count += 1
                if missing_count <= 3:  # Only log first few to avoid spam
                    logger.error(f"Metric {metric_name} not found in SweepMetrics for sweep {m.sweep_index}")
                data.append(np.nan)
        
        if missing_count > 0:
            logger.error(f"Total {missing_count} missing values for metric {metric_name}")
        
        # Log summary statistics for debugging
        valid_data = [d for d in data if not np.isnan(d)]
        if valid_data:
            logger.debug(f"Extracted {len(valid_data)} valid values for {metric_name}: "
                        f"min={min(valid_data):.2f}, max={max(valid_data):.2f}, "
                        f"mean={np.mean(valid_data):.2f}")
        else:
            logger.warning(f"No valid data extracted for {metric_name}")
        
        return data, label
    
    def _format_range_label(self, base_label: str, voltage: float) -> str:
        """Format label with voltage."""
        if np.isnan(voltage):
            return base_label
        
        rounded = int(round(voltage))
        voltage_str = f"+{rounded}" if rounded >= 0 else str(rounded)
        return f"{base_label} ({voltage_str}mV)"
    
    def _format_single_range_export(self, plot_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format single range for export."""
        headers = [plot_data.get('x_label', 'X'), plot_data.get('y_label', 'Y')]
        data = np.column_stack([plot_data['x_data'], plot_data['y_data']])
        return {'headers': headers, 'data': data, 'format_spec': '%.6f'}
    
    def _format_dual_range_export(self, plot_data: Dict[str, Any], 
                                  params: AnalysisParameters) -> Dict[str, Any]:
        """
        Format dual range for export.
        
        FIXED: Correctly handle Time axis for dual range exports.
        When X-axis is Time, use a single time column for both ranges.
        """
        # Get labels
        x_label = plot_data.get('x_label', 'X')
        
        # Get the base y_label without voltage annotation for cleaner export
        y_label = plot_data.get('y_label', 'Y')
        
        # For dual range, we can include the voltage in the label if desired
        y_label_r1 = plot_data.get('y_label_r1', f"{y_label} Range 1")
        y_label_r2 = plot_data.get('y_label_r2', f"{y_label} Range 2")
        
        # Get data arrays
        x_data = plot_data.get('x_data', np.array([]))
        y_data = plot_data.get('y_data', np.array([]))
        x_data2 = plot_data.get('x_data2', np.array([]))
        y_data2 = plot_data.get('y_data2', np.array([]))
        
        # Check if X-axis is Time
        if params.x_axis.measure == "Time":
            # Time is always the same for both ranges - use single column
            headers = [x_label, y_label_r1, y_label_r2]
            
            # Ensure all arrays are same length
            min_len = min(len(x_data), len(y_data), len(y_data2))
            if min_len != len(x_data) or min_len != len(y_data) or min_len != len(y_data2):
                logger.warning(f"Array length mismatch in dual range export: "
                              f"x={len(x_data)}, y1={len(y_data)}, y2={len(y_data2)}")
                x_data = x_data[:min_len]
                y_data = y_data[:min_len]
                y_data2 = y_data2[:min_len]
            
            data = np.column_stack([x_data, y_data, y_data2])
            
        else:
            # X-axis is Voltage or Current, which can differ between ranges
            # Check if we have different x-values for each range
            if len(x_data2) > 0 and not np.array_equal(x_data, x_data2):
                # Different x values for each range - need separate columns
                headers = [
                    f"{x_label} (Range 1)",
                    y_label_r1,
                    f"{x_label} (Range 2)",
                    y_label_r2
                ]
                
                # Pad arrays to same length if needed
                max_len = max(len(x_data), len(x_data2))
                
                # Pad range 1 data if needed
                if len(x_data) < max_len:
                    x_data = np.pad(x_data, (0, max_len - len(x_data)), constant_values=np.nan)
                    y_data = np.pad(y_data, (0, max_len - len(y_data)), constant_values=np.nan)
                
                # Pad range 2 data if needed  
                if len(x_data2) < max_len:
                    x_data2 = np.pad(x_data2, (0, max_len - len(x_data2)), constant_values=np.nan)
                    y_data2 = np.pad(y_data2, (0, max_len - len(y_data2)), constant_values=np.nan)
                
                # Create data array with separate x columns
                data = np.column_stack([x_data, y_data, x_data2, y_data2])
            else:
                # Same x values for both ranges - single x column
                headers = [x_label, y_label_r1, y_label_r2]
                
                # Ensure all arrays are same length
                min_len = min(len(x_data), len(y_data), len(y_data2))
                if min_len != len(x_data) or min_len != len(y_data) or min_len != len(y_data2):
                    logger.warning(f"Array length mismatch: x={len(x_data)}, "
                                  f"y1={len(y_data)}, y2={len(y_data2)}")
                    x_data = x_data[:min_len]
                    y_data = y_data[:min_len]
                    y_data2 = y_data2[:min_len]
                
                data = np.column_stack([x_data, y_data, y_data2])
        
        return {'headers': headers, 'data': data, 'format_spec': '%.6f'}
    
    def get_axis_label(self, axis_config: AxisConfig) -> str:
        """
        Generate axis label without extracting data.
        
        Args:
            axis_config: Axis configuration
            
        Returns:
            Formatted axis label string
        """
        if axis_config.measure == "Time":
            return "Time (s)"
        
        # Determine channel and unit
        unit = "mV" if axis_config.channel == "Voltage" else "pA"
        
        if axis_config.measure == "Average":
            return f"Average {axis_config.channel} ({unit})"
        
        elif axis_config.measure == "Peak":
            # Create descriptive label based on peak type
            peak_labels = {
                "Absolute": "Peak",
                "Positive": "Peak (+)",
                "Negative": "Peak (-)",
                "Peak-Peak": "Peak-Peak"
            }
            peak_type = axis_config.peak_type or "Absolute"
            peak_label = peak_labels.get(peak_type, "Peak")
            return f"{peak_label} {axis_config.channel} ({unit})"
        
        else:
            # Fallback
            return f"{axis_config.measure} {axis_config.channel} ({unit})"