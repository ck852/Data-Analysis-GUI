"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

"""
Test script for current density analysis workflow.

Tests the complete workflow from batch analysis through current density
calculation and export, matching exactly what the GUI does.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List
from dataclasses import replace
from copy import deepcopy

import numpy as np
import pytest

from data_analysis_gui.core.channel_definitions import ChannelDefinitions
from data_analysis_gui.core.params import AnalysisParameters, AxisConfig
from data_analysis_gui.services.batch_processor import BatchProcessor
from data_analysis_gui.services.data_manager import DataManager
from data_analysis_gui.services.current_density_service import CurrentDensityService


# Expected Cslow values for each file
CSLOW_VALUES = {
    "250514_001": 34.4,
    "250514_002": 14.5,
    "250514_003": 20.5,
    "250514_004": 16.3,
    "250514_005": 18.4,
    "250514_006": 17.3,
    "250514_007": 14.4,
    "250514_008": 14.1,
    "250514_009": 18.4,
    "250514_010": 21.0,
    "250514_011": 22.2,
    "250514_012": 23.2
}


class CurrentDensityTestBase:
    """Base class for current density workflow tests."""

    # Subclasses should define these
    FILE_TYPE = None  # 'abf' or 'mat'
    FILE_EXTENSION = None  # '*.abf' or '*.mat'

    @property
    def sample_data_dir(self) -> Path:
        """Get the sample data directory for this file type."""
        return Path(f"tests/fixtures/sample_data/IV+CD/{self.FILE_TYPE}")

    @property
    def golden_data_dir(self) -> Path:
        """Get the golden data directory for this file type."""
        return Path(f"tests/fixtures/golden_data/golden_CD/{self.FILE_TYPE}")

    @pytest.fixture
    def analysis_params(self):
        """Create analysis parameters matching the GUI state."""
        return AnalysisParameters(
            range1_start=150.1,
            range1_end=649.2,
            use_dual_range=False,
            range2_start=None,
            range2_end=None,
            stimulus_period=1000.0,
            x_axis=AxisConfig(measure="Average", channel="Voltage"),
            y_axis=AxisConfig(measure="Average", channel="Current"),
            channel_config={'voltage': 0, 'current': 1, 'current_units': 'pA'}
        )

    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        shutil.rmtree(temp_dir)

    def get_test_files(self) -> List[str]:
        """Get all test files from the sample data directory."""
        if not self.sample_data_dir.exists():
            pytest.skip(f"Sample data directory not found: {self.sample_data_dir}")

        test_files = list(self.sample_data_dir.glob(self.FILE_EXTENSION))
        if not test_files:
            pytest.skip(f"No {self.FILE_TYPE.upper()} files found in {self.sample_data_dir}")

        return [str(f) for f in sorted(test_files)]

    def test_current_density_workflow(self, analysis_params, temp_output_dir):
        """Test the complete current density analysis workflow."""
        # Initialize services (exactly as GUI does)
        channel_defs = ChannelDefinitions()
        batch_processor = BatchProcessor(channel_defs)
        data_manager = DataManager()
        cd_service = CurrentDensityService()  # GUI creates this

        # Step 1: Get all test files
        test_files = self.get_test_files()
        assert len(test_files) == 12, f"Expected 12 {self.FILE_TYPE.upper()} files, found {len(test_files)}"

        # Step 2: Perform batch analysis
        print(f"Processing {len(test_files)} {self.FILE_TYPE.upper()} files...")
        batch_result = batch_processor.process_files(
            file_paths=test_files,
            params=analysis_params
        )

        # Verify all files processed successfully
        assert len(batch_result.successful_results) == 12, \
            f"Expected 12 successful results, got {len(batch_result.successful_results)}"
        assert len(batch_result.failed_results) == 0, \
            f"Unexpected failures: {[r.file_path for r in batch_result.failed_results]}"

        # Validate Cslow values using the service (as GUI could)
        file_names = {r.base_name for r in batch_result.successful_results}
        validation_errors = cd_service.validate_cslow_values(CSLOW_VALUES, file_names)
        assert len(validation_errors) == 0, f"Cslow validation errors: {validation_errors}"

        # Step 3: Apply current density calculations (matching GUI's current_density_results_window.py)
        cd_results = []
        for result in batch_result.successful_results:
            base_name = result.base_name
            cslow = CSLOW_VALUES.get(base_name)

            assert cslow is not None and cslow > 0, f"Invalid Cslow value for {base_name}"

            # This is EXACTLY what the GUI does in _recalculate_cd_for_file():
            # It does NOT call cd_service.calculate_current_density()!
            new_y_data = np.array(result.y_data) / cslow
            
            # Update export_table with new current density values
            new_export_table = None
            if result.export_table:
                new_export_table = deepcopy(result.export_table)
                if 'data' in new_export_table:
                    data_array = np.array(new_export_table['data'])
                    if len(data_array.shape) == 2 and data_array.shape[1] >= 2:
                        # Column 1 is y_data (column 0 is x_data)
                        data_array[:, 1] = new_y_data
                        new_export_table['data'] = data_array
            
            # Add "_CD" suffix as GUI does in _export_individual_csvs()
            cd_result = replace(
                result,
                base_name=f"{result.base_name}_CD",
                y_data=new_y_data,
                export_table=new_export_table
            )
            
            # Handle dual range if present (matching GUI logic)
            if analysis_params.use_dual_range and result.y_data2 is not None:
                new_y_data2 = np.array(result.y_data2) / cslow
                
                if new_export_table and 'data' in new_export_table:
                    data_array = np.array(new_export_table['data'])
                    if data_array.shape[1] >= 3:
                        data_array[:, 2] = new_y_data2
                        new_export_table['data'] = data_array
                
                cd_result = replace(cd_result, y_data2=new_y_data2, export_table=new_export_table)
            
            cd_results.append(cd_result)

        # Create new batch result with current density values
        cd_batch_result = replace(
            batch_result,
            successful_results=cd_results,
            selected_files={r.base_name for r in cd_results}  # All files selected
        )

        # Step 4: Export individual current density CSVs
        cd_output_dir = os.path.join(temp_output_dir, "current_density")
        os.makedirs(cd_output_dir, exist_ok=True)

        export_result = batch_processor.export_results(cd_batch_result, cd_output_dir)

        assert export_result.success_count == 12, \
            f"Expected 12 successful exports, got {export_result.success_count}"
        
        # Verify files have "_CD" suffix
        exported_files = list(Path(cd_output_dir).glob("*_CD.csv"))
        assert len(exported_files) == 12, f"Expected 12 files with _CD suffix, found {len(exported_files)}"

        # Step 5: Test Summary Export using the service (as GUI does)
        # First prepare the voltage data structure like GUI does
        voltage_data = {}
        file_mapping = {}
        sorted_results = sorted(cd_results, key=lambda r: r.base_name)
        
        for idx, result in enumerate(sorted_results):
            recording_id = f"Recording {idx + 1}"
            base_name = result.base_name.replace("_CD", "")
            file_mapping[recording_id] = base_name
            
            for i, voltage in enumerate(result.x_data):
                voltage_rounded = round(float(voltage), 1)
                if voltage_rounded not in voltage_data:
                    voltage_data[voltage_rounded] = [np.nan] * len(sorted_results)
                if i < len(result.y_data):
                    voltage_data[voltage_rounded][idx] = result.y_data[i]
        
        # Use the service to prepare summary data (exactly as GUI does)
        selected_files = {r.base_name.replace("_CD", "") for r in cd_results}
        summary_data = cd_service.prepare_summary_export(
            voltage_data, 
            file_mapping, 
            CSLOW_VALUES, 
            selected_files,
            "pA/pF"
        )
        
        summary_path = os.path.join(temp_output_dir, "Current_Density_Summary.csv")
        summary_result = data_manager.export_to_csv(summary_data, summary_path)
        assert summary_result.success, f"Summary export failed: {summary_result.error_message}"

    def test_cslow_validation(self):
        """Test Cslow validation functionality using the service."""
        cd_service = CurrentDensityService()
        
        # Test the calculate_current_density method (even though GUI doesn't use it)
        current = np.array([100.0, 200.0, 300.0])
        cslow = 20.0
        cd = cd_service.calculate_current_density(current, cslow)
        
        expected = np.array([5.0, 10.0, 15.0])
        np.testing.assert_allclose(cd, expected)
        
        # Test invalid Cslow
        with pytest.raises(ValueError, match="Cslow must be positive"):
            cd_service.calculate_current_density(current, 0.0)
        
        with pytest.raises(ValueError, match="Cslow must be positive"):
            cd_service.calculate_current_density(current, -10.0)
        
        # Test validation method
        cslow_mapping = {
            "file1": 20.0,    # Valid
            "file2": 0.0,     # Invalid - zero
            "file3": -5.0,    # Invalid - negative
            "file4": 15000.0, # Invalid - too large
        }
        
        file_names = set(cslow_mapping.keys())
        errors = cd_service.validate_cslow_values(cslow_mapping, file_names)
        
        assert "file1" not in errors
        assert "file2" in errors and "must be positive" in errors["file2"]
        assert "file3" in errors and "must be positive" in errors["file3"]
        assert "file4" in errors and "unreasonably large" in errors["file4"]


class TestCurrentDensityABF(CurrentDensityTestBase):
    """Test current density workflow with ABF files."""
    FILE_TYPE = 'abf'
    FILE_EXTENSION = '*.abf'


class TestCurrentDensityMAT(CurrentDensityTestBase):
    """Test current density workflow with MAT files."""
    FILE_TYPE = 'mat'
    FILE_EXTENSION = '*.mat'


if __name__ == "__main__":
    # Run the test directly
    import sys
    sys.exit(pytest.main([__file__, "-v"]))