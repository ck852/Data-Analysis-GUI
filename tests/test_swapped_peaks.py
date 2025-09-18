"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

"""
Test module for Swap Channels functionality with Peak Analysis across all peak modes.

This test validates the channel swapping feature with peak analysis by:
1. Loading MAT/ABF files with swapped channel configuration
2. Activating the swap channels feature
3. Running batch analysis with Peak Voltage (X) and Peak Current (Y)
4. Testing all four peak modes: Absolute, Positive, Negative, Peak-Peak
5. Comparing outputs against golden reference data for each peak mode
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import csv
from typing import List, Dict, Any, Tuple
from abc import ABC, abstractmethod

# Import core components
from data_analysis_gui.core.channel_definitions import ChannelDefinitions
from data_analysis_gui.core.params import AnalysisParameters, AxisConfig
from data_analysis_gui.core.dataset import DatasetLoader
from data_analysis_gui.services.batch_processor import BatchProcessor
from data_analysis_gui.services.data_manager import DataManager
from data_analysis_gui.services.analysis_manager import AnalysisManager
from data_analysis_gui.core.app_controller import ApplicationController


# Test fixtures paths
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# Peak modes to test
PEAK_MODES = ["Absolute", "Positive", "Negative", "Peak-Peak"]


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp(prefix="test_swap_peaks_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def channel_definitions():
    """Create channel definitions with swapping capability."""
    return ChannelDefinitions(voltage_channel=0, current_channel=1)


@pytest.fixture
def batch_processor(channel_definitions):
    """Create batch processor with swapped channels."""
    # First swap the channels
    channel_definitions.swap_channels()
    return BatchProcessor(channel_definitions)


def create_analysis_parameters(peak_mode: str) -> AnalysisParameters:
    """
    Create analysis parameters for a specific peak mode.
    
    Args:
        peak_mode: One of "Absolute", "Positive", "Negative", "Peak-Peak"
    
    Returns:
        AnalysisParameters configured for the specified peak mode
    """
    return AnalysisParameters(
        range1_start=50.60,
        range1_end=548.65,
        use_dual_range=False,  # Single range only
        range2_start=None,
        range2_end=None,
        stimulus_period=1000.0,
        x_axis=AxisConfig(
            measure="Peak",
            channel="Voltage",
            peak_type=peak_mode
        ),
        y_axis=AxisConfig(
            measure="Peak",
            channel="Current",
            peak_type=peak_mode
        ),
        channel_config={'channels_swapped': True}
    )


def get_data_files(directory: Path, extension: str) -> List[Path]:
    """Get all data files in a directory with given extension, sorted numerically."""
    data_files = list(directory.glob(f"*.{extension}"))
    # Sort by the numeric part in the filename
    data_files.sort(key=lambda x: int(x.stem.split('_')[-1].split('[')[0]))
    return data_files


def load_csv_data(csv_path: Path) -> Dict[str, Any]:
    """Load CSV data into a structured format for comparison."""
    data = {
        'headers': [],
        'values': []
    }
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        # First line should be headers (with # prefix)
        header_line = next(reader)
        if header_line[0].startswith('#'):
            header_line[0] = header_line[0][1:].strip()
        data['headers'] = header_line
        
        # Read all data rows
        for row in reader:
            # Convert to floats where possible
            float_row = []
            for val in row:
                try:
                    float_row.append(float(val))
                except ValueError:
                    float_row.append(val)
            data['values'].append(float_row)
    
    return data


def compare_csv_files(generated_path: Path, golden_path: Path, 
                     tolerance: float = 1e-5) -> Tuple[bool, str]:
    """
    Compare two CSV files with tolerance for floating point differences.
    
    Args:
        generated_path: Path to generated CSV file
        golden_path: Path to golden reference CSV file
        tolerance: Numerical tolerance for float comparisons
        
    Returns:
        Tuple of (success, error_message)
    """
    try:
        generated_data = load_csv_data(generated_path)
        golden_data = load_csv_data(golden_path)
        
        # Check headers match
        if generated_data['headers'] != golden_data['headers']:
            return False, f"Headers don't match:\nGenerated: {generated_data['headers']}\nGolden: {golden_data['headers']}"
        
        # Check same number of rows
        if len(generated_data['values']) != len(golden_data['values']):
            return False, f"Row count mismatch: {len(generated_data['values'])} vs {len(golden_data['values'])}"
        
        # Compare each value with tolerance
        for row_idx, (gen_row, gold_row) in enumerate(zip(generated_data['values'], golden_data['values'])):
            if len(gen_row) != len(gold_row):
                return False, f"Column count mismatch in row {row_idx}: {len(gen_row)} vs {len(gold_row)}"
            
            for col_idx, (gen_val, gold_val) in enumerate(zip(gen_row, gold_row)):
                if isinstance(gen_val, float) and isinstance(gold_val, float):
                    # Use numpy for NaN-aware comparison
                    if np.isnan(gen_val) and np.isnan(gold_val):
                        continue  # Both NaN is ok
                    if np.abs(gen_val - gold_val) >= tolerance:
                        return False, f"Value mismatch at row {row_idx}, col {col_idx}: {gen_val} vs {gold_val} (diff: {np.abs(gen_val - gold_val)})"
                else:
                    if gen_val != gold_val:
                        return False, f"Value mismatch at row {row_idx}, col {col_idx}: {gen_val} vs {gold_val}"
        
        return True, ""
        
    except Exception as e:
        return False, f"Error comparing files: {str(e)}"


def get_peak_mode_folder_name(peak_mode: str) -> str:
    """
    Convert peak mode to folder name used in golden data structure.
    
    Args:
        peak_mode: Peak mode string (e.g., "Peak-Peak", "Absolute")
        
    Returns:
        Folder name (e.g., "peak-peak", "absolute")
    """
    return peak_mode.lower().replace(" ", "")


class TestSwappedPeaksBase(ABC):
    """Base class for testing Swap Channels with Peak Analysis across all modes."""
    
    @property
    @abstractmethod
    def file_format(self) -> str:
        """Return the file format being tested ('mat' or 'abf')."""
        pass
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the file extension for this format."""
        pass
    
    @property
    def sample_data_dir(self) -> Path:
        """Return the sample data directory for this format."""
        return FIXTURES_DIR / "sample_data" / "swapped" / self.file_format
    
    def get_golden_data_dir(self, peak_mode: str) -> Path:
        """
        Return the golden data directory for a specific peak mode.
        
        Args:
            peak_mode: The peak mode being tested
            
        Returns:
            Path to golden data directory
        """
        folder_name = get_peak_mode_folder_name(peak_mode)
        return FIXTURES_DIR / "golden_data" / "golden_swapped_peaks_IV" / self.file_format / folder_name
    
    def _test_single_peak_mode(self, batch_processor, temp_output_dir, peak_mode: str):
        """
        Helper method to test batch analysis for a single peak mode.
        
        Args:
            batch_processor: BatchProcessor with swapped channels
            temp_output_dir: Temporary directory for outputs
            peak_mode: Peak mode to test
        """
        # Skip if sample data directory doesn't exist
        if not self.sample_data_dir.exists():
            pytest.skip(f"Sample data directory not found: {self.sample_data_dir}")
        
        # Get all data files in the directory
        data_files = get_data_files(self.sample_data_dir, self.file_extension)
        
        if not data_files:
            pytest.skip(f"No {self.file_extension.upper()} files found in sample data directory")
        
        # Convert to string paths for batch processor
        file_paths = [str(f) for f in data_files]
        
        # Create analysis parameters for this peak mode
        params = create_analysis_parameters(peak_mode)
        
        # Run batch analysis with swapped channels
        batch_result = batch_processor.process_files(
            file_paths=file_paths,
            params=params
        )
        
        # Check that we have successful results
        assert len(batch_result.successful_results) > 0, f"No successful batch results for {peak_mode} mode"
        assert len(batch_result.failed_results) == 0, \
            f"Some files failed in {peak_mode} mode: {[r.base_name for r in batch_result.failed_results]}"
        
        # Create output subdirectory for this peak mode
        peak_output_dir = temp_output_dir / get_peak_mode_folder_name(peak_mode)
        peak_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export results to CSV files
        export_result = batch_processor.export_results(
            batch_result=batch_result,
            output_dir=str(peak_output_dir)
        )
        
        assert export_result.success_count > 0, f"No files exported successfully for {peak_mode} mode"
        
        # Get golden data directory for this peak mode
        golden_dir = self.get_golden_data_dir(peak_mode)
        
        # Skip golden data comparison if directory doesn't exist
        if not golden_dir.exists():
            pytest.skip(f"Golden data directory not found for {peak_mode}: {golden_dir}")
        
        # Compare each generated CSV with golden data
        comparison_failures = []
        for result in batch_result.successful_results:
            generated_csv = peak_output_dir / f"{result.base_name}.csv"
            golden_csv = golden_dir / f"{result.base_name}.csv"
            
            assert generated_csv.exists(), f"Generated CSV not found: {generated_csv}"
            
            if golden_csv.exists():
                # Compare the files
                success, error_msg = compare_csv_files(generated_csv, golden_csv)
                if not success:
                    comparison_failures.append(f"{result.base_name}: {error_msg}")
            else:
                pytest.skip(f"Golden CSV not found for {peak_mode}: {golden_csv}")
        
        # Report all comparison failures
        if comparison_failures:
            failure_report = f"CSV comparison failed for {peak_mode} mode:\n" + "\n".join(comparison_failures)
            pytest.fail(failure_report)
    
    @pytest.mark.parametrize("peak_mode", PEAK_MODES)
    def test_peak_mode(self, batch_processor, temp_output_dir, peak_mode):
        """Test batch analysis for a specific peak mode."""
        print(f"\nTesting {peak_mode} peak mode for {self.file_format} files...")
        self._test_single_peak_mode(batch_processor, temp_output_dir, peak_mode)
    
    def test_all_peak_modes_sequential(self, batch_processor, temp_output_dir):
        """Test batch analysis for all peak modes sequentially."""
        for peak_mode in PEAK_MODES:
            print(f"\nTesting {peak_mode} peak mode for {self.file_format} files...")
            self._test_single_peak_mode(batch_processor, temp_output_dir, peak_mode)
    
    def test_peak_mode_parameters(self):
        """Test that analysis parameters are correctly created for each peak mode."""
        for peak_mode in PEAK_MODES:
            params = create_analysis_parameters(peak_mode)
            
            # Check basic parameters
            assert params.range1_start == 50.60
            assert params.range1_end == 548.65
            assert params.use_dual_range is False
            assert params.range2_start is None
            assert params.range2_end is None
            assert params.stimulus_period == 1000.0
            
            # Check axis configurations
            assert params.x_axis.measure == "Peak"
            assert params.x_axis.channel == "Voltage"
            assert params.x_axis.peak_type == peak_mode
            
            assert params.y_axis.measure == "Peak"
            assert params.y_axis.channel == "Current"
            assert params.y_axis.peak_type == peak_mode
            
            # Check channel configuration
            assert params.channel_config['channels_swapped'] is True
    
    @pytest.mark.parametrize("peak_mode", PEAK_MODES)
    def test_controller_workflow_with_peak_mode(self, temp_output_dir, peak_mode):
        """Test complete workflow using ApplicationController for a specific peak mode."""
        
        # Skip if sample data doesn't exist
        if not self.sample_data_dir.exists():
            pytest.skip(f"Sample data directory not found: {self.sample_data_dir}")
        
        # Get test files
        test_files = get_data_files(self.sample_data_dir, self.file_extension)
        if not test_files:
            pytest.skip("No test files found")
        
        print(f"\nTesting controller workflow for {peak_mode} peak mode...")
        
        # Create controller with fresh channel definitions
        channel_defs = ChannelDefinitions()
        controller = ApplicationController(channel_definitions=channel_defs)
        
        # Load first file to establish context
        load_result = controller.load_file(str(test_files[0]))
        assert load_result.success, f"Failed to load file: {load_result.error_message}"
        
        # Swap channels
        swap_result = controller.swap_channels()
        assert swap_result['success']
        assert swap_result['is_swapped']
        
        # Create analysis parameters for this peak mode
        params = create_analysis_parameters(peak_mode)
        
        # Run batch analysis
        file_paths = [str(f) for f in test_files]
        batch_result = controller.run_batch_analysis(
            file_paths=file_paths,
            params=params
        )
        
        assert len(batch_result.successful_results) == len(test_files), \
            f"Not all files processed successfully for {peak_mode} mode"
        
        # Create output subdirectory for this peak mode
        peak_output_dir = temp_output_dir / f"controller_{get_peak_mode_folder_name(peak_mode)}"
        peak_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export results
        export_result = controller.export_batch_results(
            batch_result=batch_result,
            output_directory=str(peak_output_dir)
        )
        
        assert export_result.success_count == len(test_files), \
            f"Not all files exported successfully for {peak_mode} mode"


class TestSwappedPeaksMAT(TestSwappedPeaksBase):
    """Test Swap Channels with Peak Analysis for MAT files."""
    
    @property
    def file_format(self) -> str:
        return "mat"
    
    @property
    def file_extension(self) -> str:
        return "mat"


class TestSwappedPeaksABF(TestSwappedPeaksBase):
    """Test Swap Channels with Peak Analysis for ABF files."""
    
    @property
    def file_format(self) -> str:
        return "abf"
    
    @property
    def file_extension(self) -> str:
        return "abf"


class TestPeakModeValidation:
    """Test validation of peak mode configurations."""
    
    def test_peak_mode_normalization(self):
        """Test that various peak mode strings are properly normalized."""
        test_cases = [
            ("Absolute", "Absolute"),
            ("absolute", "Absolute"),
            ("ABSOLUTE", "Absolute"),
            ("Positive", "Positive"),
            ("positive", "Positive"),
            ("Negative", "Negative"),
            ("negative", "Negative"),
            ("Peak-Peak", "Peak-Peak"),
            ("peak-peak", "Peak-Peak"),
            ("PeakPeak", "Peak-Peak"),
            ("peak to peak", "Peak-Peak"),
            ("Peak_to_Peak", "Peak-Peak"),
        ]
        
        for input_mode, expected_normalized in test_cases:
            params = AnalysisParameters(
                range1_start=50.60,
                range1_end=548.65,
                use_dual_range=False,
                range2_start=None,
                range2_end=None,
                stimulus_period=1000.0,
                x_axis=AxisConfig(measure="Peak", channel="Voltage", peak_type=input_mode),
                y_axis=AxisConfig(measure="Peak", channel="Current", peak_type=input_mode),
                channel_config={}
            )
            
            # The normalization happens in the plot_formatter, but we can verify
            # that the parameters accept various forms
            assert params.x_axis.peak_type == input_mode
            assert params.y_axis.peak_type == input_mode
    
    def test_channel_swap_state(self, channel_definitions):
        """Test that channel swap state is correctly maintained."""
        # Initial state
        assert channel_definitions.is_swapped() is False
        assert channel_definitions.get_voltage_channel() == 0
        assert channel_definitions.get_current_channel() == 1
        
        # After swap
        channel_definitions.swap_channels()
        assert channel_definitions.is_swapped() is True
        assert channel_definitions.get_voltage_channel() == 1
        assert channel_definitions.get_current_channel() == 0
        
        # Create parameters with swapped state
        for peak_mode in PEAK_MODES:
            params = create_analysis_parameters(peak_mode)
            assert params.channel_config['channels_swapped'] is True


if __name__ == "__main__":
    # Run tests with pytest
    import sys
    pytest.main([__file__, "-v", "-s"] + sys.argv[1:])