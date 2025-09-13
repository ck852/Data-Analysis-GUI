"""
Test module for Swap Channels functionality with batch analysis.

This test validates the channel swapping feature by:
1. Loading MAT files with swapped channel configuration
2. Activating the swap channels feature
3. Running batch analysis with specific parameters
4. Comparing outputs against golden reference data
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import tempfile
import shutil
import csv
from typing import List, Dict, Any

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
SAMPLE_DATA_DIR = FIXTURES_DIR / "sample_data" / "swapped" / "mat"
GOLDEN_DATA_DIR = FIXTURES_DIR / "golden_data" / "golden_mat_swapped"


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for test outputs."""
    temp_dir = tempfile.mkdtemp(prefix="test_swap_channels_")
    yield Path(temp_dir)
    # Cleanup after test
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def channel_definitions():
    """Create channel definitions with swapping capability."""
    return ChannelDefinitions(voltage_channel=0, current_channel=1)


@pytest.fixture
def analysis_parameters():
    """Create analysis parameters matching the test requirements."""
    return AnalysisParameters(
        range1_start=50.60,
        range1_end=548.65,
        use_dual_range=True,
        range2_start=550.65,
        range2_end=648.85,
        stimulus_period=1000.0,
        x_axis=AxisConfig(
            measure="Time",
            channel=None,  # Time doesn't need a channel
            peak_type=None
        ),
        y_axis=AxisConfig(
            measure="Average",
            channel="Current",
            peak_type=None
        ),
        channel_config={'channels_swapped': True}
    )


@pytest.fixture
def batch_processor(channel_definitions):
    """Create batch processor with swapped channels."""
    # First swap the channels
    channel_definitions.swap_channels()
    return BatchProcessor(channel_definitions)


@pytest.fixture
def controller(channel_definitions):
    """Create application controller with channel definitions."""
    return ApplicationController(channel_definitions=channel_definitions)


def get_mat_files(directory: Path) -> List[Path]:
    """Get all MAT files in a directory, sorted numerically."""
    mat_files = list(directory.glob("*.mat"))
    # Sort by the numeric part in the filename
    mat_files.sort(key=lambda x: int(x.stem.split('_')[-1].split('[')[0]))
    return mat_files


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


def compare_csv_files(generated_path: Path, golden_path: Path, tolerance: float = 1e-6) -> bool:
    """
    Compare two CSV files with tolerance for floating point differences.
    
    Args:
        generated_path: Path to generated CSV file
        golden_path: Path to golden reference CSV file
        tolerance: Numerical tolerance for float comparisons
        
    Returns:
        True if files match within tolerance
    """
    generated_data = load_csv_data(generated_path)
    golden_data = load_csv_data(golden_path)
    
    # Check headers match
    assert generated_data['headers'] == golden_data['headers'], \
        f"Headers don't match:\nGenerated: {generated_data['headers']}\nGolden: {golden_data['headers']}"
    
    # Check same number of rows
    assert len(generated_data['values']) == len(golden_data['values']), \
        f"Row count mismatch: {len(generated_data['values'])} vs {len(golden_data['values'])}"
    
    # Compare each value with tolerance
    for row_idx, (gen_row, gold_row) in enumerate(zip(generated_data['values'], golden_data['values'])):
        assert len(gen_row) == len(gold_row), \
            f"Column count mismatch in row {row_idx}: {len(gen_row)} vs {len(gold_row)}"
        
        for col_idx, (gen_val, gold_val) in enumerate(zip(gen_row, gold_row)):
            if isinstance(gen_val, float) and isinstance(gold_val, float):
                # Use numpy for NaN-aware comparison
                if np.isnan(gen_val) and np.isnan(gold_val):
                    continue  # Both NaN is ok
                assert np.abs(gen_val - gold_val) < tolerance, \
                    f"Value mismatch at row {row_idx}, col {col_idx}: {gen_val} vs {gold_val}"
            else:
                assert gen_val == gold_val, \
                    f"Value mismatch at row {row_idx}, col {col_idx}: {gen_val} vs {gold_val}"
    
    return True


class TestSwapChannels:
    """Test suite for Swap Channels functionality with batch analysis."""
    
    def test_single_file_swap_channels(self, controller, analysis_parameters):
        """Test channel swapping on a single file."""
        # Load a single test file
        test_file = SAMPLE_DATA_DIR / "240809_001[1-12].mat"
        
        # Skip if test file doesn't exist
        if not test_file.exists():
            pytest.skip(f"Test file not found: {test_file}")
        
        # Load the file
        result = controller.load_file(str(test_file))
        assert result.success, f"Failed to load file: {result.error_message}"
        
        # Verify file loaded correctly
        assert controller.has_data()
        
        # Swap channels
        swap_result = controller.swap_channels()
        assert swap_result['success'], f"Failed to swap channels: {swap_result.get('reason')}"
        assert swap_result['is_swapped'] is True
        
        # Perform analysis with swapped channels
        analysis_result = controller.perform_analysis(analysis_parameters)
        assert analysis_result.success, f"Analysis failed: {analysis_result.error_message}"
        
        # Verify we have results
        assert analysis_result.data is not None
        assert len(analysis_result.data.x_data) > 0
        assert len(analysis_result.data.y_data) > 0
    
    def test_batch_analysis_with_swapped_channels(self, batch_processor, analysis_parameters, temp_output_dir):
        """Test batch analysis with swapped channels and compare to golden data."""
        
        # Skip if sample data directory doesn't exist
        if not SAMPLE_DATA_DIR.exists():
            pytest.skip(f"Sample data directory not found: {SAMPLE_DATA_DIR}")
        
        # Get all MAT files in the directory
        mat_files = get_mat_files(SAMPLE_DATA_DIR)
        
        if not mat_files:
            pytest.skip("No MAT files found in sample data directory")
        
        # Convert to string paths for batch processor
        file_paths = [str(f) for f in mat_files]
        
        # Run batch analysis with swapped channels
        batch_result = batch_processor.process_files(
            file_paths=file_paths,
            params=analysis_parameters,
            parallel=False  # Use sequential for deterministic results
        )
        
        # Check that we have successful results
        assert len(batch_result.successful_results) > 0, "No successful batch results"
        assert len(batch_result.failed_results) == 0, \
            f"Some files failed: {[r.base_name for r in batch_result.failed_results]}"
        
        # Export results to CSV files
        export_result = batch_processor.export_results(
            batch_result=batch_result,
            output_dir=str(temp_output_dir)
        )
        
        assert export_result.success_count > 0, "No files exported successfully"
        
        # Skip golden data comparison if directory doesn't exist
        if not GOLDEN_DATA_DIR.exists():
            pytest.skip(f"Golden data directory not found: {GOLDEN_DATA_DIR}")
        
        # Compare each generated CSV with golden data
        for result in batch_result.successful_results:
            generated_csv = temp_output_dir / f"{result.base_name}.csv"
            golden_csv = GOLDEN_DATA_DIR / f"{result.base_name}.csv"
            
            assert generated_csv.exists(), f"Generated CSV not found: {generated_csv}"
            
            if golden_csv.exists():
                # Compare the files
                assert compare_csv_files(generated_csv, golden_csv), \
                    f"CSV comparison failed for {result.base_name}"
            else:
                pytest.skip(f"Golden CSV not found: {golden_csv}")
    
    def test_swap_channels_state_persistence(self, channel_definitions):
        """Test that channel swap state persists correctly."""
        # Initial state
        assert channel_definitions.is_swapped() is False
        assert channel_definitions.get_voltage_channel() == 0
        assert channel_definitions.get_current_channel() == 1
        
        # Swap channels
        channel_definitions.swap_channels()
        assert channel_definitions.is_swapped() is True
        assert channel_definitions.get_voltage_channel() == 1
        assert channel_definitions.get_current_channel() == 0
        
        # Swap back
        channel_definitions.swap_channels()
        assert channel_definitions.is_swapped() is False
        assert channel_definitions.get_voltage_channel() == 0
        assert channel_definitions.get_current_channel() == 1
    
    def test_analysis_parameters_with_dual_range(self, analysis_parameters):
        """Test that analysis parameters are correctly configured for dual range."""
        assert analysis_parameters.use_dual_range is True
        assert analysis_parameters.range1_start == 50.60
        assert analysis_parameters.range1_end == 548.65
        assert analysis_parameters.range2_start == 550.65
        assert analysis_parameters.range2_end == 648.85
        assert analysis_parameters.stimulus_period == 1000.0
        
        # Check axis configurations
        assert analysis_parameters.x_axis.measure == "Time"
        assert analysis_parameters.x_axis.channel is None
        assert analysis_parameters.y_axis.measure == "Average"
        assert analysis_parameters.y_axis.channel == "Current"
    
    def test_batch_processor_with_parallel_processing(self, batch_processor, analysis_parameters, temp_output_dir):
        """Test batch processing with parallel execution."""
        
        # Skip if sample data directory doesn't exist
        if not SAMPLE_DATA_DIR.exists():
            pytest.skip(f"Sample data directory not found: {SAMPLE_DATA_DIR}")
        
        # Get subset of files for faster parallel test
        mat_files = get_mat_files(SAMPLE_DATA_DIR)[:3]  # Test with first 3 files
        
        if not mat_files:
            pytest.skip("No MAT files found in sample data directory")
        
        file_paths = [str(f) for f in mat_files]
        
        # Run parallel batch analysis
        batch_result = batch_processor.process_files(
            file_paths=file_paths,
            params=analysis_parameters,
            parallel=True,
            max_workers=2
        )
        
        # Verify results
        assert len(batch_result.successful_results) == len(mat_files)
        assert batch_result.processing_time > 0
        
        # Export and verify files were created
        export_result = batch_processor.export_results(
            batch_result=batch_result,
            output_dir=str(temp_output_dir)
        )
        
        for result in batch_result.successful_results:
            csv_path = temp_output_dir / f"{result.base_name}.csv"
            assert csv_path.exists(), f"CSV not created for {result.base_name}"


# Integration test that uses the full application controller
class TestSwapChannelsIntegration:
    """Integration tests for Swap Channels with full application flow."""
    
    def test_full_workflow_with_controller(self, temp_output_dir):
        """Test complete workflow using ApplicationController."""
        
        # Skip if sample data doesn't exist
        if not SAMPLE_DATA_DIR.exists():
            pytest.skip(f"Sample data directory not found: {SAMPLE_DATA_DIR}")
        
        # Create controller with fresh channel definitions
        channel_defs = ChannelDefinitions()
        controller = ApplicationController(channel_definitions=channel_defs)
        
        # Load first file to establish context
        test_files = get_mat_files(SAMPLE_DATA_DIR)
        if not test_files:
            pytest.skip("No test files found")
        
        # Load a file
        load_result = controller.load_file(str(test_files[0]))
        assert load_result.success
        
        # Swap channels
        swap_result = controller.swap_channels()
        assert swap_result['success']
        assert swap_result['is_swapped']
        
        # Create analysis parameters
        params = AnalysisParameters(
            range1_start=50.60,
            range1_end=548.65,
            use_dual_range=True,
            range2_start=550.65,
            range2_end=648.85,
            stimulus_period=1000.0,
            x_axis=AxisConfig(measure="Time", channel=None),
            y_axis=AxisConfig(measure="Average", channel="Current"),
            channel_config={'channels_swapped': True}
        )
        
        # Run batch analysis
        file_paths = [str(f) for f in test_files]
        batch_result = controller.run_batch_analysis(
            file_paths=file_paths,
            params=params,
            parallel=False
        )
        
        assert len(batch_result.successful_results) == len(test_files)
        
        # Export results
        export_result = controller.export_batch_results(
            batch_result=batch_result,
            output_directory=str(temp_output_dir)
        )
        
        assert export_result.success_count == len(test_files)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])