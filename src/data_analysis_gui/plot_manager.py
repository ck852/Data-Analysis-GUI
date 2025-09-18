from __future__ import annotations
"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

"""
Improved plot management module for MAT File Sweep Analyzer.

This version uses Qt signals for complete decoupling from the main window.
PlotManager is now purely responsible for matplotlib visualization and
emits neutral signals about plot interactions.
"""

import logging
from typing import Optional, List, Tuple, Dict, Any

import numpy as np
from matplotlib.axes import Axes
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout

from data_analysis_gui.config.plot_style import (
    apply_plot_style, format_sweep_plot, get_line_styles
)
from data_analysis_gui.widgets.custom_toolbar import StreamlinedNavigationToolbar


# Set up a logger for better debugging
logger = logging.getLogger(__name__)


class PlotManager(QObject):
    """
    Manages all plotting operations, including sweep plots, range lines, and interactions.

    This class encapsulates a Matplotlib Figure and its associated canvas and toolbar,
    providing a clean interface for plotting data and emitting signals about user
    interactions. It has NO knowledge of the main window or any external widgets.
    """
    
    # Define signals for plot interactions
    # Signal: (action, line_id, value)
    # Actions: 'dragged', 'added', 'removed', 'centered'
    line_state_changed = Signal(str, str, float)
    
    # Signal for plot updates
    plot_updated = Signal()

    def __init__(self, figure_size: Tuple[int, int] = (8, 6)):
        """
        Initializes the plot manager with modern styling.
        """
        super().__init__()
        
        # Apply modern plot style globally
        apply_plot_style()
        
        # Get line styles for consistent appearance
        self.line_styles = get_line_styles()
        
        # 1. Matplotlib components setup with styled figure
        self.figure: Figure = Figure(figsize=figure_size, facecolor='#FAFAFA')
        self.canvas: FigureCanvas = FigureCanvas(self.figure)
        self.ax: Axes = self.figure.add_subplot(111)
        
        # Use the streamlined toolbar instead of standard NavigationToolbar
        self.toolbar: StreamlinedNavigationToolbar = StreamlinedNavigationToolbar(
            self.canvas, None
        )

        # Create the plot widget
        self.plot_widget: QWidget = QWidget()
        plot_layout: QVBoxLayout = QVBoxLayout(self.plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(0)
        plot_layout.addWidget(self.toolbar)
        plot_layout.addWidget(self.canvas)

        # 2. Range lines management
        self.range_lines: List[Line2D] = []
        self._line_ids: Dict[Line2D, str] = {}
        self._initialize_range_lines()

        # 3. Interactivity state
        self.dragging_line: Optional[Line2D] = None

        # 4. Connect interactive events
        self._connect_events()
        
        # 5. Apply initial styling to axes
        self._style_axes()

    def _style_axes(self):
        """Apply modern styling to the axes with updated font sizes."""
        self.ax.set_facecolor('#FAFBFC')
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['left'].set_linewidth(0.8)
        self.ax.spines['bottom'].set_linewidth(0.8)
        self.ax.spines['left'].set_color('#B0B0B0')
        self.ax.spines['bottom'].set_color('#B0B0B0')
        
        # Use the increased font sizes from plot_style
        self.ax.tick_params(
            axis='both',
            which='major',
            labelsize=9,
            colors='#606060',
            length=4,
            width=0.8
        )
        
        self.ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5, color='#E1E5E8')
        self.ax.set_axisbelow(True)

    def get_plot_widget(self) -> QWidget:
        """Returns the QWidget containing the plot canvas and toolbar."""
        return self.plot_widget

    def _connect_events(self) -> None:
        """Connects mouse events to their respective handlers for interactivity."""
        self.canvas.mpl_connect("pick_event", self._on_pick)
        self.canvas.mpl_connect("motion_notify_event", self._on_drag)
        self.canvas.mpl_connect("button_release_event", self._on_release)

    def _initialize_range_lines(self) -> None:
        """Initializes range lines with modern styling."""
        self.range_lines.clear()
        self._line_ids.clear()

        # Use styled colors for range lines
        range1_style = self.line_styles['range1']
        
        line1 = self.ax.axvline(
            150, 
            color=range1_style['color'],
            linestyle=range1_style['linestyle'],
            linewidth=range1_style['linewidth'],
            alpha=range1_style['alpha'],
            picker=5
        )
        line2 = self.ax.axvline(
            500,
            color=range1_style['color'],
            linestyle=range1_style['linestyle'],
            linewidth=range1_style['linewidth'],
            alpha=range1_style['alpha'],
            picker=5
        )
        
        self.range_lines.extend([line1, line2])
        self._line_ids[line1] = 'range1_start'
        self._line_ids[line2] = 'range1_end'
        
        self.line_state_changed.emit('added', 'range1_start', 150)
        self.line_state_changed.emit('added', 'range1_end', 500)
        
        logger.debug("Initialized styled range lines.")

    def update_sweep_plot(
        self,
        t: np.ndarray,
        y: np.ndarray,
        channel: int,
        sweep_index: int,
        channel_type: str,
        channel_config: Optional[dict] = None,
        title: Optional[str] = None,
        x_label: Optional[str] = None,
        y_label: Optional[str] = None,
    ) -> None:
        """
        Updates the plot with new sweep data using modern styling.
        Now accepts optional title and labels for consistency.
        """
        self.ax.clear()

        # Plot with modern styling
        line_style = self.line_styles['primary']
        self.ax.plot(
            t, y[:, channel],
            color=line_style['color'],
            linewidth=line_style['linewidth'],
            alpha=line_style['alpha']
        )

        # Apply sweep-specific formatting with custom labels if provided
        if title or x_label or y_label:
            # Use custom labels/title
            from data_analysis_gui.config.plot_style import style_axis
            style_axis(self.ax, title=title, xlabel=x_label, ylabel=y_label)
            self.ax.set_facecolor('#FAFBFC')  # Keep sweep plot background
        else:
            # Use default formatting
            format_sweep_plot(self.ax, sweep_index, channel_type)

        # Restore range lines with consistent styling
        for line in self.range_lines:
            self.ax.add_line(line)

        # Apply padding for better visualization
        self.ax.relim()
        self.ax.autoscale_view(tight=True)
        self.ax.margins(x=0.02, y=0.05)

        self.figure.tight_layout(pad=1.0)
        self.redraw()
        self.plot_updated.emit()
        logger.info(f"Updated plot for sweep {sweep_index}, channel {channel}.")

    def update_range_lines(
        self,
        start1: float,
        end1: float,
        use_dual_range: bool = False,
        start2: Optional[float] = None,
        end2: Optional[float] = None,
    ) -> None:
        """Updates range lines with proper styling."""
        # Get style configurations
        range1_style = self.line_styles['range1']
        range2_style = self.line_styles['range2']
        
        # Ensure we have at least 2 lines for Range 1
        if len(self.range_lines) < 2:
            if len(self.range_lines) == 0:
                line1 = self.ax.axvline(
                    start1,
                    color=range1_style['color'],
                    linestyle=range1_style['linestyle'],
                    linewidth=range1_style['linewidth'],
                    alpha=range1_style['alpha'],
                    picker=5
                )
                line2 = self.ax.axvline(
                    end1,
                    color=range1_style['color'],
                    linestyle=range1_style['linestyle'],
                    linewidth=range1_style['linewidth'],
                    alpha=range1_style['alpha'],
                    picker=5
                )
                self.range_lines.extend([line1, line2])
                self._line_ids[line1] = 'range1_start'
                self._line_ids[line2] = 'range1_end'
            elif len(self.range_lines) == 1:
                line2 = self.ax.axvline(
                    end1,
                    color=range1_style['color'],
                    linestyle=range1_style['linestyle'],
                    linewidth=range1_style['linewidth'],
                    alpha=range1_style['alpha'],
                    picker=5
                )
                self.range_lines.append(line2)
                self._line_ids[line2] = 'range1_end'
        else:
            # Update existing Range 1 lines
            self.range_lines[0].set_xdata([start1, start1])
            self.range_lines[1].set_xdata([end1, end1])

        has_second_range = len(self.range_lines) == 4
        
        if use_dual_range and start2 is not None and end2 is not None:
            if not has_second_range:
                # Add Range 2 lines with different styling
                line3 = self.ax.axvline(
                    start2,
                    color=range2_style['color'],
                    linestyle=range2_style['linestyle'],
                    linewidth=range2_style['linewidth'],
                    alpha=range2_style['alpha'],
                    picker=5
                )
                line4 = self.ax.axvline(
                    end2,
                    color=range2_style['color'],
                    linestyle=range2_style['linestyle'],
                    linewidth=range2_style['linewidth'],
                    alpha=range2_style['alpha'],
                    picker=5
                )
                
                self.range_lines.extend([line3, line4])
                self._line_ids[line3] = 'range2_start'
                self._line_ids[line4] = 'range2_end'
                
                self.line_state_changed.emit('added', 'range2_start', start2)
                self.line_state_changed.emit('added', 'range2_end', end2)
            else:
                # Update existing Range 2 lines
                self.range_lines[2].set_xdata([start2, start2])
                self.range_lines[3].set_xdata([end2, end2])
        elif not use_dual_range and has_second_range:
            # Remove Range 2 lines
            line4 = self.range_lines.pop()
            line3 = self.range_lines.pop()
            
            self.line_state_changed.emit('removed', self._line_ids.get(line3, 'range2_start'), line3.get_xdata()[0])
            self.line_state_changed.emit('removed', self._line_ids.get(line4, 'range2_end'), line4.get_xdata()[0])
            
            if line3 in self._line_ids:
                del self._line_ids[line3]
            if line4 in self._line_ids:
                del self._line_ids[line4]
            
            if line3.axes:
                line3.remove()
            if line4.axes:
                line4.remove()

        self.redraw()
        logger.debug("Updated range lines with modern styling.")

    def center_nearest_cursor(self) -> Tuple[Optional[str], Optional[float]]:
        """
        Finds the horizontal center of the current plot view and moves the nearest
        range line to that position.

        Returns:
            A tuple containing the line ID that was moved and its new
            x-position, or (None, None) if no action was taken.
        """
        if not self.range_lines or not self.ax.has_data():
            logger.warning("Cannot center cursor: No range lines or data available.")
            return None, None

        x_min, x_max = self.ax.get_xlim()
        center_x = (x_min + x_max) / 2

        # Find the line closest to the center of the view
        distances = [abs(line.get_xdata()[0] - center_x) for line in self.range_lines]
        nearest_idx = int(np.argmin(distances))
        nearest_line = self.range_lines[nearest_idx]
        line_id = self._line_ids.get(nearest_line, f'line_{nearest_idx}')

        # Move the line
        nearest_line.set_xdata([center_x, center_x])

        logger.info(f"Centered nearest cursor to x={center_x:.2f}.")

        # Emit signal about the centering
        self.line_state_changed.emit('centered', line_id, center_x)

        self.redraw()

        return line_id, center_x

    # --- Mouse Interaction Handlers ---

    def _on_pick(self, event) -> None:
        """Handles pick events to initiate dragging a line."""
        if isinstance(event.artist, Line2D) and event.artist in self.range_lines:
            self.dragging_line = event.artist
            logger.debug(f"Picked line: {self._line_ids.get(self.dragging_line, 'unknown')}.")

    def _on_drag(self, event) -> None:
        """Handles mouse motion events to drag a selected line."""
        if self.dragging_line and event.xdata is not None:
            x_pos = float(event.xdata)
            self.dragging_line.set_xdata([x_pos, x_pos])
            
            # Emit signal about the drag
            line_id = self._line_ids.get(self.dragging_line, 'unknown')
            self.line_state_changed.emit('dragged', line_id, x_pos)
            
            self.redraw()

    def _on_release(self, event) -> None:
        """Handles mouse release events to conclude a drag operation."""
        if self.dragging_line:
            line_id = self._line_ids.get(self.dragging_line, 'unknown')
            x_pos = self.dragging_line.get_xdata()[0]
            logger.debug(f"Released line {line_id} at x={x_pos:.2f}.")
            self.dragging_line = None

    def clear(self) -> None:
        """Clears the plot axes completely."""
        # Clear axes - this removes all artists including lines
        self.ax.clear()
        
        # Reset line tracking (don't try to remove already-removed lines)
        self.range_lines.clear()
        self._line_ids.clear()
        
        # Re-add default range lines
        line1 = self.ax.axvline(150, color='green', linestyle='-', picker=5, linewidth=2)
        line2 = self.ax.axvline(500, color='green', linestyle='-', picker=5, linewidth=2)
        
        self.range_lines.extend([line1, line2])
        self._line_ids[line1] = 'range1_start'
        self._line_ids[line2] = 'range1_end'
        
        self.line_state_changed.emit('added', 'range1_start', 150)
        self.line_state_changed.emit('added', 'range1_end', 500)
        
        self.redraw()
        self.plot_updated.emit()
        logger.info("Plot cleared.")

    def redraw(self) -> None:
        """Forces a redraw of the plot canvas."""
        self.canvas.draw_idle()

    def update_lines_from_values(
        self,
        start1: float,
        end1: float,
        use_dual_range: bool = False,
        start2: Optional[float] = None,
        end2: Optional[float] = None,
    ) -> None:
        """
        Updates range line positions without recreating them.
        This method maintains compatibility with the existing interface.
        
        Args:
            start1: Start position for range 1
            end1: End position for range 1
            use_dual_range: Whether dual range is active
            start2: Start position for range 2 (if dual range)
            end2: End position for range 2 (if dual range)
        """
        # Delegate to the main update method
        self.update_range_lines(start1, end1, use_dual_range, start2, end2)

    def toggle_dual_range(self, enabled: bool, start2: float, end2: float) -> None:
        """
        Toggle dual range visualization.
        
        Args:
            enabled: Whether to enable dual range
            start2: Start position for range 2
            end2: End position for range 2
        """
        if enabled:
            # Get current range 1 values
            start1 = self.range_lines[0].get_xdata()[0] if self.range_lines else 150
            end1 = self.range_lines[1].get_xdata()[0] if len(self.range_lines) > 1 else 500
            
            # Update with dual range
            self.update_range_lines(start1, end1, True, start2, end2)
        else:
            # Get current range 1 values
            start1 = self.range_lines[0].get_xdata()[0] if self.range_lines else 150
            end1 = self.range_lines[1].get_xdata()[0] if len(self.range_lines) > 1 else 500
            
            # Update without dual range
            self.update_range_lines(start1, end1, False, None, None)

    def get_line_positions(self) -> Dict[str, float]:
        """
        Get current positions of all range lines.
        
        Returns:
            Dictionary mapping line IDs to their x positions
        """
        positions = {}
        for line, line_id in self._line_ids.items():
            positions[line_id] = line.get_xdata()[0]
        return positions

    @staticmethod
    def setup_plot_style(ax: Axes, title: str = "", xlabel: str = "", 
                        ylabel: str = "", grid: bool = True) -> None:
        """Configure plot appearance with larger font sizes."""
        # Use the style_axis function from plot_style which has the updated font sizes
        from data_analysis_gui.config.plot_style import style_axis
        style_axis(ax, title=title, xlabel=xlabel, ylabel=ylabel)
        
        if grid:
            ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)

    @staticmethod
    def add_padding_to_axes(ax: Axes, x_padding_pct: float = 0.05, 
                        y_padding_pct: float = 0.05) -> None:
        """Add padding to plot axes."""
        x_min, x_max = ax.get_xlim()
        y_min, y_max = ax.get_ylim()
        
        x_range = x_max - x_min
        y_range = y_max - y_min
        
        x_padding = x_range * x_padding_pct if x_range > 0 else 0.1
        y_padding = y_range * y_padding_pct if y_range > 0 else 0.1
        
        ax.set_xlim(x_min - x_padding, x_max + x_padding)
        ax.set_ylim(y_min - y_padding, y_max + y_padding)

    def clear_plot(self) -> None:
        """Alias for clear() to maintain backward compatibility."""
        self.clear()


class BatchPlotter:
    """
    Provides static methods for creating non-interactive batch plots.

    By making these static, we separate the concern of creating one-off batch plots
    from the stateful management of the main interactive plot.
    """

    @staticmethod
    def create_figure(
        x_label: str,
        y_label: str,
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 6)
    ) -> Tuple[Figure, Axes]:
        """
        Creates a new Figure and Axes for a batch plot with updated font sizes.

        Args:
            x_label: The label for the x-axis.
            y_label: The label for the y-axis.
            title: The plot title. If None, a default is generated.
            figsize: A tuple for the figure size (width, height) in inches.

        Returns:
            A tuple containing the created Matplotlib Figure and Axes.
        """
        fig = Figure(figsize=figsize, tight_layout=True)
        ax = fig.add_subplot(111)
        
        # Use style_axis for consistent font sizes
        from data_analysis_gui.config.plot_style import style_axis
        style_axis(
            ax,
            title=title or f"{y_label} vs {x_label}",
            xlabel=x_label,
            ylabel=y_label
        )
        
        ax.grid(True, which='both', linestyle='--', alpha=0.5)
        return fig, ax

    @staticmethod
    def plot_data(
        ax: Axes, x_data: np.ndarray, y_data: np.ndarray, label: str,
        marker: str = 'o-', **kwargs
    ) -> None:
        """
        Plots a data series on the given Axes.

        Args:
            ax: The Matplotlib Axes to plot on.
            x_data: The data for the x-axis.
            y_data: The data for the y-axis.
            label: The legend label for the data series.
            marker: The marker and line style.
            **kwargs: Additional keyword arguments passed to ax.plot().
        """
        if x_data.size > 0 and y_data.size > 0:
            ax.plot(x_data, y_data, marker, label=label, **kwargs)
        else:
            logger.warning(f"Attempted to plot empty data for label '{label}'.")

    @staticmethod
    def finalize_plot(fig: Figure, ax: Axes) -> None:
        """
        Finalizes a batch plot by adding a legend with proper font size.

        Args:
            fig: The Matplotlib Figure.
            ax: The Matplotlib Axes.
        """
        if ax.get_legend_handles_labels()[0]:
            # Legend font size is now handled by the rcParams in plot_style
            ax.legend()
        logger.info("Finalized batch plot.")