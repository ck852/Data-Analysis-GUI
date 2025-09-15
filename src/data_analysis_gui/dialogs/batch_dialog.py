# dialogs/batch_dialog.py

from pathlib import Path
from typing import List, Optional
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QListWidget, QProgressBar, QLabel, QCheckBox,
                             QDialogButtonBox, QMessageBox,
                             QAbstractItemView, QGroupBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal

from data_analysis_gui.gui_services import FileDialogService
from data_analysis_gui.core.models import FileAnalysisResult, BatchAnalysisResult
from data_analysis_gui.config.logging import get_logger
from data_analysis_gui.config.themes import (
    style_dialog, apply_compact_layout, style_list_widget, 
    style_progress_bar, style_group_box, style_checkbox, 
    style_status_label, get_file_count_color, create_styled_button
)

logger = get_logger(__name__)

# Default number of workers for parallel processing
DEFAULT_MAX_WORKERS = 4


class BatchAnalysisWorker(QThread):
    """Worker thread for batch analysis."""
    progress = pyqtSignal(int, int, str)
    file_complete = pyqtSignal(object)  # FileAnalysisResult
    finished = pyqtSignal(object)  # BatchAnalysisResult
    error = pyqtSignal(str)
    
    def __init__(self, batch_service, file_paths, params, parallel):
        super().__init__()
        self.batch_service = batch_service
        self.file_paths = file_paths
        self.params = params
        self.parallel = parallel
    
    def run(self):
        """Run batch analysis in thread."""
        try:
            # Set up progress callbacks
            self.batch_service.on_progress = lambda c, t, n: self.progress.emit(c, t, n)
            self.batch_service.on_file_complete = lambda r: self.file_complete.emit(r)
            
            result = self.batch_service.process_files(
                self.file_paths, 
                self.params, 
                self.parallel, 
                DEFAULT_MAX_WORKERS
            )
            
            # Ensure result has selection state initialized
            if not hasattr(result, 'selected_files') or result.selected_files is None:
                from dataclasses import replace
                result = replace(
                    result,
                    selected_files={r.base_name for r in result.successful_results}
                )
            
            self.finished.emit(result)
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}", exc_info=True)
            self.error.emit(str(e))


class BatchAnalysisDialog(QDialog):
    """Dialog for batch analysis with progress tracking."""
    
    def __init__(self, parent, batch_service, params):
        super().__init__(parent)
        self.batch_service = batch_service
        self.params = params
        self.file_paths = []
        self.worker = None
        self.batch_result = None
        
        # Initialize services
        self.file_dialog_service = FileDialogService()
        
        self.init_ui()
        
        # Apply theme and layout helpers from themes.py
        style_dialog(self, "Batch Analysis")
        apply_compact_layout(self)
    
    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        
        # File List Section
        file_group = QGroupBox("Files to Analyze")
        style_group_box(file_group)
        file_group_layout = QVBoxLayout(file_group)
        
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        style_list_widget(self.file_list)
        file_group_layout.addWidget(self.file_list)
        
        self.file_count_label = QLabel("0 files selected")
        style_status_label(self.file_count_label, 'muted')
        file_group_layout.addWidget(self.file_count_label)
        
        layout.addWidget(file_group)
        
        # File Management Buttons
        file_button_layout = QHBoxLayout()
        self.add_files_btn = create_styled_button("Add Files...", "secondary", self)
        self.remove_selected_btn = create_styled_button("Remove Selected", "secondary", self)
        self.clear_all_btn = create_styled_button("Clear All", "secondary", self)
        
        file_button_layout.addWidget(self.add_files_btn)
        file_button_layout.addWidget(self.remove_selected_btn)
        file_button_layout.addWidget(self.clear_all_btn)
        file_button_layout.addStretch()
        layout.addLayout(file_button_layout)
        
        # Processing Options
        options_group = QGroupBox("Processing Options")
        style_group_box(options_group)
        options_layout = QHBoxLayout(options_group)
        
        self.parallel_checkbox = QCheckBox("Parallel Processing")
        self.parallel_checkbox.setChecked(True)
        style_checkbox(self.parallel_checkbox)
        options_layout.addWidget(self.parallel_checkbox)
        options_layout.addStretch()
        layout.addWidget(options_group)
        
        # Progress Section
        progress_group = QGroupBox("Progress")
        style_group_box(progress_group)
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        style_progress_bar(self.progress_bar)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        style_status_label(self.status_label, 'muted')
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Action Buttons
        button_layout = QHBoxLayout()
        
        self.analyze_btn = create_styled_button("Start Analysis", "primary", self)
        self.cancel_btn = create_styled_button("Cancel", "secondary", self)
        self.cancel_btn.setEnabled(False)
        self.view_results_btn = create_styled_button("View Results", "accent", self)
        self.view_results_btn.setEnabled(False)
        self.close_btn = create_styled_button("Close", "secondary", self)
        
        button_layout.addWidget(self.analyze_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addWidget(self.view_results_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Connect signals
        self.add_files_btn.clicked.connect(self.add_files)
        self.remove_selected_btn.clicked.connect(self.remove_selected)
        self.clear_all_btn.clicked.connect(self.clear_files)
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.cancel_btn.clicked.connect(self.cancel_analysis)
        self.view_results_btn.clicked.connect(self.view_results)
        self.close_btn.clicked.connect(self.close)
        
        # Update button states
        self.update_button_states()
    
    def add_files(self):
        """Add files to the batch list."""
        file_types = (
            "Data files (*.mat *.abf);;"
            "MAT files (*.mat);;"
            "ABF files (*.abf);;"
            "All files (*.*)"
        )
        
        default_dir = None
        if hasattr(self.parent(), 'current_file_path'):
            current_path = self.parent().current_file_path
            if current_path:
                default_dir = str(Path(current_path).parent)
        
        file_paths = self.file_dialog_service.get_import_paths(
            self, 
            "Select Files for Batch Analysis",
            default_dir,
            file_types
        )
        
        if file_paths:
            for file_path in file_paths:
                if file_path not in self.file_paths:
                    self.file_paths.append(file_path)
                    self.file_list.addItem(Path(file_path).name)
            
            self.update_file_count()
            self.update_button_states()
    
    def remove_selected(self):
        """Remove selected files from the batch list."""
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            return
        
        for item in reversed(selected_items):
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
            del self.file_paths[row]
        
        self.update_file_count()
        self.update_button_states()
    
    def clear_files(self):
        """Clear all files from the batch list."""
        self.file_list.clear()
        self.file_paths.clear()
        self.update_file_count()
        self.update_button_states()
    
    def update_file_count(self):
        """Update the file count label using theme utilities."""
        count = len(self.file_paths)
        self.file_count_label.setText(f"{count} file{'s' if count != 1 else ''} selected")
        
        color = get_file_count_color(count)
        self.file_count_label.setStyleSheet(f"color: {color};")
    
    def update_button_states(self):
        """Update button enabled states based on current state."""
        has_files = len(self.file_paths) > 0
        is_running = self.worker is not None and self.worker.isRunning()
        has_results = self.batch_result is not None
        
        self.add_files_btn.setEnabled(not is_running)
        self.remove_selected_btn.setEnabled(not is_running and has_files)
        self.clear_all_btn.setEnabled(not is_running and has_files)
        self.analyze_btn.setEnabled(not is_running and has_files)
        self.cancel_btn.setEnabled(is_running)
        self.view_results_btn.setEnabled(has_results)
        self.parallel_checkbox.setEnabled(not is_running)
    
    def start_analysis(self):
        """Start the batch analysis."""
        if not self.file_paths:
            QMessageBox.warning(self, "No Files", "Please add files to analyze.")
            return
        
        # Reset progress
        self.progress_bar.setMaximum(len(self.file_paths))
        self.progress_bar.setValue(0)
        style_status_label(self.status_label, 'info')
        self.status_label.setText("Starting analysis...")
        
        # Create and start worker thread
        self.worker = BatchAnalysisWorker(
            self.batch_service,
            self.file_paths.copy(),
            self.params,
            self.parallel_checkbox.isChecked()
        )
        
        # Connect worker signals
        self.worker.progress.connect(self.on_progress)
        self.worker.file_complete.connect(self.on_file_complete)
        self.worker.finished.connect(self.on_analysis_finished)
        self.worker.error.connect(self.on_error)
        
        # Start analysis
        self.worker.start()
        self.update_button_states()
        logger.info(f"Started batch analysis of {len(self.file_paths)} files")
    
    def cancel_analysis(self):
        """Cancel the running analysis."""
        if self.worker and self.worker.isRunning():
            self.worker.quit()
            self.worker.wait()
            style_status_label(self.status_label, 'warning')
            self.status_label.setText("Analysis cancelled")
            self.update_button_states()
    
    def on_progress(self, completed, total, current_file):
        """Handle progress updates from worker."""
        self.progress_bar.setValue(completed)
        style_status_label(self.status_label, 'info')
        self.status_label.setText(f"Processing {current_file} ({completed}/{total})")
    
    def on_file_complete(self, result: FileAnalysisResult):
        """Handle completion of individual file."""
        status = "✓" if result.success else "✗"
        logger.debug(f"{status} Completed: {result.base_name}")
    
    def on_analysis_finished(self, result: BatchAnalysisResult):
        """Handle completion of batch analysis."""
        self.batch_result = result
        
        success_count = len(result.successful_results)
        fail_count = len(result.failed_results)
        total_time = result.processing_time
        
        if fail_count > 0:
            status_msg = f"Complete: {success_count} succeeded, {fail_count} failed in {total_time:.1f}s"
            style_status_label(self.status_label, 'warning')
        else:
            status_msg = f"Complete: {success_count} files analyzed in {total_time:.1f}s"
            style_status_label(self.status_label, 'success')
        
        self.status_label.setText(status_msg)
        self.update_button_states()
        logger.info(f"Batch analysis complete: {result.success_rate:.1f}% success rate")
    
    def on_error(self, error_msg):
        """Handle errors from worker."""
        QMessageBox.critical(self, "Analysis Error", f"Batch analysis failed:\n{error_msg}")
        style_status_label(self.status_label, 'error')
        self.status_label.setText("Analysis failed")
        self.update_button_states()
    
    def view_results(self):
        """Open the results window."""
        if not self.batch_result:
            return
        
        try:
            from data_analysis_gui.dialogs.batch_results_window import BatchResultsWindow
            from data_analysis_gui.services.plot_service import PlotService
            
            plot_service = PlotService()
            
            results_window = BatchResultsWindow(
                self,
                self.batch_result,
                self.batch_service,
                plot_service,
                self.parent().controller.data_service
            )
            results_window.show()
            
        except Exception as e:
            logger.error(f"Failed to show results: {e}", exc_info=True)
            QMessageBox.critical(self, "Error", f"Failed to display results:\n{str(e)}")