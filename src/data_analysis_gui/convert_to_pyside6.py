#!/usr/bin/env python3
"""
PyQt5 to PySide6 Conversion Script
Run from the src folder (data_analysis_gui/)
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import defaultdict

class PyQt5ToPySide6Converter:
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.files_processed = 0
        self.changes_made = defaultdict(int)
        self.warnings = []
        self.errors = []
        
        # Define all conversion patterns
        self.setup_conversion_patterns()
    
    def setup_conversion_patterns(self):
        """Define all the conversion patterns needed"""
        
        # Basic import replacements
        self.import_replacements = [
            (r'from PyQt5\.QtWidgets import', 'from PySide6.QtWidgets import'),
            (r'from PyQt5\.QtCore import', 'from PySide6.QtCore import'),
            (r'from PyQt5\.QtGui import', 'from PySide6.QtGui import'),
            (r'from PySide6 import QtWidgets', 'from PySide6 import QtWidgets'),
            (r'from PySide6 import QtCore', 'from PySide6 import QtCore'),
            (r'from PySide6 import QtGui', 'from PySide6 import QtGui'),
            (r'import PyQt5\.QtWidgets', 'import PySide6.QtWidgets'),
            (r'import PyQt5\.QtCore', 'import PySide6.QtCore'),
            (r'import PyQt5\.QtGui', 'import PySide6.QtGui'),
        ]
        
        # Signal replacement - needs special handling to add Signal to imports
        self.signal_pattern = r'\bpyqtSignal\b'
        
        # Matplotlib backend replacement
        self.matplotlib_replacements = [
            (r'from matplotlib\.backends\.backend_qt5agg import FigureCanvas',
             'from matplotlib.backends.backend_qtagg import FigureCanvas'),
            (r'from matplotlib\.backends\.backend_qt5agg import NavigationToolbar',
             'from matplotlib.backends.backend_qtagg import NavigationToolbar'),
            (r'FigureCanvas\b', 'FigureCanvas'),
            (r'NavigationToolbar\b', 'NavigationToolbar'),
        ]
        
        # Qt enum patterns that need namespace updates
        # Format: (pattern, replacement)
        self.qt_enum_patterns = [
            # Window states
            (r'\bQt\.WindowNoState\b', 'Qt.WindowState.WindowNoState'),
            (r'\bQt\.WindowMinimized\b', 'Qt.WindowState.WindowMinimized'),
            (r'\bQt\.WindowMaximized\b', 'Qt.WindowState.WindowMaximized'),
            (r'\bQt\.WindowFullScreen\b', 'Qt.WindowState.WindowFullScreen'),
            (r'\bQt\.WindowActive\b', 'Qt.WindowState.WindowActive'),
            
            # Application attributes
            (r'\bQt\.AA_EnableHighDpiScaling\b', 'Qt.ApplicationAttribute.AA_EnableHighDpiScaling'),
            (r'\bQt\.AA_UseHighDpiPixmaps\b', 'Qt.ApplicationAttribute.AA_UseHighDpiPixmaps'),
            
            # Alignment flags
            (r'\bQt\.AlignLeft\b', 'Qt.AlignmentFlag.AlignLeft'),
            (r'\bQt\.AlignRight\b', 'Qt.AlignmentFlag.AlignRight'),
            (r'\bQt\.AlignCenter\b', 'Qt.AlignmentFlag.AlignCenter'),
            (r'\bQt\.AlignTop\b', 'Qt.AlignmentFlag.AlignTop'),
            (r'\bQt\.AlignBottom\b', 'Qt.AlignmentFlag.AlignBottom'),
            (r'\bQt\.AlignHCenter\b', 'Qt.AlignmentFlag.AlignHCenter'),
            (r'\bQt\.AlignVCenter\b', 'Qt.AlignmentFlag.AlignVCenter'),
            
            # Orientations
            (r'\bQt\.Horizontal\b', 'Qt.Orientation.Horizontal'),
            (r'\bQt\.Vertical\b', 'Qt.Orientation.Vertical'),
            
            # Mouse buttons
            (r'\bQt\.LeftButton\b', 'Qt.MouseButton.LeftButton'),
            (r'\bQt\.RightButton\b', 'Qt.MouseButton.RightButton'),
            (r'\bQt\.MiddleButton\b', 'Qt.MouseButton.MiddleButton'),
            
            # Key codes
            (r'\bQt\.Key_(\w+)\b', r'Qt.Key.Key_\1'),
            
            # Item flags
            (r'\bQt\.ItemIsEnabled\b', 'Qt.ItemFlag.ItemIsEnabled'),
            (r'\bQt\.ItemIsSelectable\b', 'Qt.ItemFlag.ItemIsSelectable'),
            (r'\bQt\.ItemIsEditable\b', 'Qt.ItemFlag.ItemIsEditable'),
            (r'\bQt\.ItemIsDragEnabled\b', 'Qt.ItemFlag.ItemIsDragEnabled'),
            (r'\bQt\.ItemIsDropEnabled\b', 'Qt.ItemFlag.ItemIsDropEnabled'),
            
            # Cursor shapes
            (r'\bQt\.ArrowCursor\b', 'Qt.CursorShape.ArrowCursor'),
            (r'\bQt\.PointingHandCursor\b', 'Qt.CursorShape.PointingHandCursor'),
            (r'\bQt\.CrossCursor\b', 'Qt.CursorShape.CrossCursor'),
            (r'\bQt\.WaitCursor\b', 'Qt.CursorShape.WaitCursor'),
            (r'\bQt\.IBeamCursor\b', 'Qt.CursorShape.IBeamCursor'),
            (r'\bQt\.SizeVerCursor\b', 'Qt.CursorShape.SizeVerCursor'),
            (r'\bQt\.SizeHorCursor\b', 'Qt.CursorShape.SizeHorCursor'),
            (r'\bQt\.SizeBDiagCursor\b', 'Qt.CursorShape.SizeBDiagCursor'),
            (r'\bQt\.SizeFDiagCursor\b', 'Qt.CursorShape.SizeFDiagCursor'),
            (r'\bQt\.SizeAllCursor\b', 'Qt.CursorShape.SizeAllCursor'),
            (r'\bQt\.BlankCursor\b', 'Qt.CursorShape.BlankCursor'),
            (r'\bQt\.SplitVCursor\b', 'Qt.CursorShape.SplitVCursor'),
            (r'\bQt\.SplitHCursor\b', 'Qt.CursorShape.SplitHCursor'),
            (r'\bQt\.ClosedHandCursor\b', 'Qt.CursorShape.ClosedHandCursor'),
            (r'\bQt\.OpenHandCursor\b', 'Qt.CursorShape.OpenHandCursor'),
            (r'\bQt\.WhatsThisCursor\b', 'Qt.CursorShape.WhatsThisCursor'),
            (r'\bQt\.BusyCursor\b', 'Qt.CursorShape.BusyCursor'),
            
            # Checkbox states
            (r'\bQt\.Unchecked\b', 'Qt.CheckState.Unchecked'),
            (r'\bQt\.PartiallyChecked\b', 'Qt.CheckState.PartiallyChecked'),
            (r'\bQt\.Checked\b', 'Qt.CheckState.Checked'),
            
            # Focus reasons
            (r'\bQt\.MouseFocusReason\b', 'Qt.FocusReason.MouseFocusReason'),
            (r'\bQt\.TabFocusReason\b', 'Qt.FocusReason.TabFocusReason'),
            (r'\bQt\.BacktabFocusReason\b', 'Qt.FocusReason.BacktabFocusReason'),
            (r'\bQt\.ActiveWindowFocusReason\b', 'Qt.FocusReason.ActiveWindowFocusReason'),
            (r'\bQt\.PopupFocusReason\b', 'Qt.FocusReason.PopupFocusReason'),
            (r'\bQt\.ShortcutFocusReason\b', 'Qt.FocusReason.ShortcutFocusReason'),
            (r'\bQt\.MenuBarFocusReason\b', 'Qt.FocusReason.MenuBarFocusReason'),
            (r'\bQt\.OtherFocusReason\b', 'Qt.FocusReason.OtherFocusReason'),
            
            # Tool button styles
            (r'\bQt\.ToolButtonIconOnly\b', 'Qt.ToolButtonStyle.ToolButtonIconOnly'),
            (r'\bQt\.ToolButtonTextOnly\b', 'Qt.ToolButtonStyle.ToolButtonTextOnly'),
            (r'\bQt\.ToolButtonTextBesideIcon\b', 'Qt.ToolButtonStyle.ToolButtonTextBesideIcon'),
            (r'\bQt\.ToolButtonTextUnderIcon\b', 'Qt.ToolButtonStyle.ToolButtonTextUnderIcon'),
            
            # Brush styles
            (r'\bQt\.NoBrush\b', 'Qt.BrushStyle.NoBrush'),
            (r'\bQt\.SolidPattern\b', 'Qt.BrushStyle.SolidPattern'),
            
            # Color roles
            (r'\bQt\.black\b', 'Qt.GlobalColor.black'),
            (r'\bQt\.white\b', 'Qt.GlobalColor.white'),
            (r'\bQt\.red\b', 'Qt.GlobalColor.red'),
            (r'\bQt\.green\b', 'Qt.GlobalColor.green'),
            (r'\bQt\.blue\b', 'Qt.GlobalColor.blue'),
            (r'\bQt\.transparent\b', 'Qt.GlobalColor.transparent'),
            
            # Selection behaviors
            (r'\bQAbstractItemView\.ExtendedSelection\b', 'QAbstractItemView.SelectionBehavior.ExtendedSelection'),
            (r'\bQAbstractItemView\.SelectRows\b', 'QAbstractItemView.SelectionBehavior.SelectRows'),
            
            # Slider tick positions
            (r'\bQSlider\.NoTicks\b', 'QSlider.TickPosition.NoTicks'),
            (r'\bQSlider\.TicksAbove\b', 'QSlider.TickPosition.TicksAbove'),
            (r'\bQSlider\.TicksBelow\b', 'QSlider.TickPosition.TicksBelow'),
            (r'\bQSlider\.TicksBothSides\b', 'QSlider.TickPosition.TicksBothSides'),
            
            # Standard keys
            (r'\bevent\.StandardKey\.(\w+)\b', r'event.StandardKey.\1'),
            (r'\bQKeySequence\.StandardKey\.(\w+)\b', r'QKeySequence.StandardKey.\1'),
        ]
        
        # QKeySequence patterns
        self.qkeysequence_patterns = [
            (r'\bQKeySequence\.Open\b', 'QKeySequence.StandardKey.Open'),
            (r'\bQKeySequence\.Save\b', 'QKeySequence.StandardKey.Save'),
            (r'\bQKeySequence\.Quit\b', 'QKeySequence.StandardKey.Quit'),
            (r'\bQKeySequence\.Copy\b', 'QKeySequence.StandardKey.Copy'),
            (r'\bQKeySequence\.Paste\b', 'QKeySequence.StandardKey.Paste'),
        ]
        
        # QDialogButtonBox patterns
        self.qdialogbuttonbox_patterns = [
            (r'\bQDialogButtonBox\.Ok\b', 'QDialogButtonBox.StandardButton.Ok'),
            (r'\bQDialogButtonBox\.Cancel\b', 'QDialogButtonBox.StandardButton.Cancel'),
            (r'\bQDialogButtonBox\.Save\b', 'QDialogButtonBox.StandardButton.Save'),
            (r'\bQDialogButtonBox\.Open\b', 'QDialogButtonBox.StandardButton.Open'),
            (r'\bQDialogButtonBox\.Close\b', 'QDialogButtonBox.StandardButton.Close'),
            (r'\bQDialogButtonBox\.Apply\b', 'QDialogButtonBox.StandardButton.Apply'),
            (r'\bQDialogButtonBox\.Reset\b', 'QDialogButtonBox.StandardButton.Reset'),
            (r'\bQDialogButtonBox\.RestoreDefaults\b', 'QDialogButtonBox.StandardButton.RestoreDefaults'),
            (r'\bQDialogButtonBox\.Help\b', 'QDialogButtonBox.StandardButton.Help'),
            (r'\bQDialogButtonBox\.SaveAll\b', 'QDialogButtonBox.StandardButton.SaveAll'),
            (r'\bQDialogButtonBox\.Yes\b', 'QDialogButtonBox.StandardButton.Yes'),
            (r'\bQDialogButtonBox\.YesToAll\b', 'QDialogButtonBox.StandardButton.YesToAll'),
            (r'\bQDialogButtonBox\.No\b', 'QDialogButtonBox.StandardButton.No'),
            (r'\bQDialogButtonBox\.NoToAll\b', 'QDialogButtonBox.StandardButton.NoToAll'),
            (r'\bQDialogButtonBox\.Abort\b', 'QDialogButtonBox.StandardButton.Abort'),
            (r'\bQDialogButtonBox\.Retry\b', 'QDialogButtonBox.StandardButton.Retry'),
            (r'\bQDialogButtonBox\.Ignore\b', 'QDialogButtonBox.StandardButton.Ignore'),
        ]
        
        # QHeaderView patterns
        self.qheaderview_patterns = [
            (r'\bQHeaderView\.Fixed\b', 'QHeaderView.ResizeMode.Fixed'),
            (r'\bQHeaderView\.Stretch\b', 'QHeaderView.ResizeMode.Stretch'),
            (r'\bQHeaderView\.Interactive\b', 'QHeaderView.ResizeMode.Interactive'),
            (r'\bQHeaderView\.ResizeToContents\b', 'QHeaderView.ResizeMode.ResizeToContents'),
        ]
        
        # QFileDialog patterns
        self.qfiledialog_patterns = [
            (r'\bQFileDialog\.ShowDirsOnly\b', 'QFileDialog.Option.ShowDirsOnly'),
            (r'\bQFileDialog\.DontResolveSymlinks\b', 'QFileDialog.Option.DontResolveSymlinks'),
            (r'\bQFileDialog\.DontConfirmOverwrite\b', 'QFileDialog.Option.DontConfirmOverwrite'),
            (r'\bQFileDialog\.DontUseNativeDialog\b', 'QFileDialog.Option.DontUseNativeDialog'),
            (r'\bQFileDialog\.ReadOnly\b', 'QFileDialog.Option.ReadOnly'),
            (r'\bQFileDialog\.HideNameFilterDetails\b', 'QFileDialog.Option.HideNameFilterDetails'),
        ]
        
        # QPalette patterns
        self.qpalette_patterns = [
            (r'\bQPalette\.Window\b', 'QPalette.ColorRole.Window'),
            (r'\bQPalette\.WindowText\b', 'QPalette.ColorRole.WindowText'),
            (r'\bQPalette\.Base\b', 'QPalette.ColorRole.Base'),
            (r'\bQPalette\.AlternateBase\b', 'QPalette.ColorRole.AlternateBase'),
            (r'\bQPalette\.Text\b', 'QPalette.ColorRole.Text'),
            (r'\bQPalette\.Button\b', 'QPalette.ColorRole.Button'),
            (r'\bQPalette\.ButtonText\b', 'QPalette.ColorRole.ButtonText'),
            (r'\bQPalette\.Highlight\b', 'QPalette.ColorRole.Highlight'),
            (r'\bQPalette\.HighlightedText\b', 'QPalette.ColorRole.HighlightedText'),
        ]
        
        # QStandardPaths patterns
        self.qstandardpaths_patterns = [
            (r'\bQStandardPaths\.AppConfigLocation\b', 'QStandardPaths.StandardLocation.AppConfigLocation'),
            (r'\bQStandardPaths\.AppDataLocation\b', 'QStandardPaths.StandardLocation.AppDataLocation'),
            (r'\bQStandardPaths\.AppLocalDataLocation\b', 'QStandardPaths.StandardLocation.AppLocalDataLocation'),
            (r'\bQStandardPaths\.CacheLocation\b', 'QStandardPaths.StandardLocation.CacheLocation'),
            (r'\bQStandardPaths\.ConfigLocation\b', 'QStandardPaths.StandardLocation.ConfigLocation'),
            (r'\bQStandardPaths\.DataLocation\b', 'QStandardPaths.StandardLocation.DataLocation'),
            (r'\bQStandardPaths\.DesktopLocation\b', 'QStandardPaths.StandardLocation.DesktopLocation'),
            (r'\bQStandardPaths\.DocumentsLocation\b', 'QStandardPaths.StandardLocation.DocumentsLocation'),
            (r'\bQStandardPaths\.DownloadLocation\b', 'QStandardPaths.StandardLocation.DownloadLocation'),
            (r'\bQStandardPaths\.GenericCacheLocation\b', 'QStandardPaths.StandardLocation.GenericCacheLocation'),
            (r'\bQStandardPaths\.GenericConfigLocation\b', 'QStandardPaths.StandardLocation.GenericConfigLocation'),
            (r'\bQStandardPaths\.GenericDataLocation\b', 'QStandardPaths.StandardLocation.GenericDataLocation'),
            (r'\bQStandardPaths\.HomeLocation\b', 'QStandardPaths.StandardLocation.HomeLocation'),
            (r'\bQStandardPaths\.MoviesLocation\b', 'QStandardPaths.StandardLocation.MoviesLocation'),
            (r'\bQStandardPaths\.MusicLocation\b', 'QStandardPaths.StandardLocation.MusicLocation'),
            (r'\bQStandardPaths\.PicturesLocation\b', 'QStandardPaths.StandardLocation.PicturesLocation'),
            (r'\bQStandardPaths\.PublicShareLocation\b', 'QStandardPaths.StandardLocation.PublicShareLocation'),
            (r'\bQStandardPaths\.RuntimeLocation\b', 'QStandardPaths.StandardLocation.RuntimeLocation'),
            (r'\bQStandardPaths\.TempLocation\b', 'QStandardPaths.StandardLocation.TempLocation'),
        ]
        
        # QPainter patterns
        self.qpainter_patterns = [
            (r'\bQPainter\.Antialiasing\b', 'QPainter.RenderHint.Antialiasing'),
            (r'\bQPainter\.TextAntialiasing\b', 'QPainter.RenderHint.TextAntialiasing'),
            (r'\bQPainter\.SmoothPixmapTransform\b', 'QPainter.RenderHint.SmoothPixmapTransform'),
        ]
        
        # QSizePolicy patterns
        self.qsizepolicy_patterns = [
            (r'\bQSizePolicy\.Fixed\b', 'QSizePolicy.Policy.Fixed'),
            (r'\bQSizePolicy\.Minimum\b', 'QSizePolicy.Policy.Minimum'),
            (r'\bQSizePolicy\.Maximum\b', 'QSizePolicy.Policy.Maximum'),
            (r'\bQSizePolicy\.Preferred\b', 'QSizePolicy.Policy.Preferred'),
            (r'\bQSizePolicy\.Expanding\b', 'QSizePolicy.Policy.Expanding'),
            (r'\bQSizePolicy\.MinimumExpanding\b', 'QSizePolicy.Policy.MinimumExpanding'),
            (r'\bQSizePolicy\.Ignored\b', 'QSizePolicy.Policy.Ignored'),
        ]
        
    def fix_signal_imports(self, content: str) -> str:
        """Fix Signal imports and usage"""
        # Check if file uses Signal
        if 'Signal' not in content:
            return content
        
        # Find the QtCore import line
        import_patterns = [
            r'from PyQt5\.QtCore import (.*)',
            r'from PySide6\.QtCore import (.*)'  # In case we're re-running
        ]
        
        for pattern in import_patterns:
            match = re.search(pattern, content)
            if match:
                imports = match.group(1)
                # Check if Signal is already imported
                if 'Signal' not in imports and 'Signal' in imports:
                    # Replace Signal with Signal in imports
                    new_imports = imports.replace('Signal', 'Signal')
                    content = content.replace(match.group(0), f'from PySide6.QtCore import {new_imports}'), Signal
                    self.changes_made['signal_import'] += 1
                elif 'Signal' not in imports:
                    # Add Signal to imports
                    new_imports = imports + ', Signal'
                    content = content.replace(match.group(0), f'from PySide6.QtCore import {new_imports}'), Signal
                    self.changes_made['signal_import'] += 1
                break
        
        # Replace Signal with Signal in the code
        if 'Signal' in content:
            content = re.sub(self.signal_pattern, 'Signal', content)
            self.changes_made['signal_usage'] += 1
        
        return content
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single Python file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Skip if no PyQt5 content
            if 'PyQt5' not in original_content and 'Signal' not in original_content:
                return False
            
            content = original_content
            
            # Apply basic import replacements
            for pattern, replacement in self.import_replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['imports'] += 1
            
            # Fix signal imports and usage
            content = self.fix_signal_imports(content)
            
            # Apply matplotlib replacements
            for pattern, replacement in self.matplotlib_replacements:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['matplotlib'] += 1
            
            # Apply Qt enum patterns
            for pattern, replacement in self.qt_enum_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qt_enums'] += 1
            
            # Apply QKeySequence patterns
            for pattern, replacement in self.qkeysequence_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qkeysequence'] += 1
            
            # Apply QDialogButtonBox patterns
            for pattern, replacement in self.qdialogbuttonbox_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qdialogbuttonbox'] += 1
            
            # Apply QHeaderView patterns
            for pattern, replacement in self.qheaderview_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qheaderview'] += 1
            
            # Apply QFileDialog patterns
            for pattern, replacement in self.qfiledialog_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qfiledialog'] += 1
            
            # Apply QPalette patterns
            for pattern, replacement in self.qpalette_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qpalette'] += 1
            
            # Apply QStandardPaths patterns
            for pattern, replacement in self.qstandardpaths_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qstandardpaths'] += 1
            
            # Apply QPainter patterns
            for pattern, replacement in self.qpainter_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qpainter'] += 1
            
            # Apply QSizePolicy patterns
            for pattern, replacement in self.qsizepolicy_patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    self.changes_made['qsizepolicy'] += 1
            
            # Check for any remaining PyQt5 references
            if 'PyQt5' in content:
                self.warnings.append(f"{filepath}: Still contains PyQt5 references after conversion")
            
            # Write the file if changes were made
            if content != original_content:
                if not self.dry_run:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                self.files_processed += 1
                return True
            
            return False
            
        except Exception as e:
            self.errors.append(f"{filepath}: {str(e)}")
            return False
    
    def process_directory(self, directory: Path) -> None:
        """Process all Python files in directory recursively"""
        python_files = list(directory.rglob('*.py'))
        
        print(f"Found {len(python_files)} Python files to process")
        print("=" * 60)
        
        for filepath in python_files:
            relative_path = filepath.relative_to(directory)
            if self.process_file(filepath):
                print(f"✓ Converted: {relative_path}")
            else:
                if 'PyQt5' in open(filepath, 'r').read() or 'Signal' in open(filepath, 'r').read():
                    print(f"⚠ Check: {relative_path}")
    
    def print_summary(self):
        """Print conversion summary"""
        print("\n" + "=" * 60)
        print("CONVERSION SUMMARY")
        print("=" * 60)
        
        print(f"\nFiles processed: {self.files_processed}")
        
        if self.changes_made:
            print("\nChanges made:")
            for change_type, count in sorted(self.changes_made.items()):
                print(f"  {change_type}: {count}")
        
        if self.warnings:
            print(f"\n⚠ Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  - {warning}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"  - {error}")
        
        if not self.warnings and not self.errors:
            print("\n✅ Conversion completed successfully!")
        else:
            print("\n⚠️ Conversion completed with warnings/errors. Please review the files mentioned above.")
        
        if self.dry_run:
            print("\n(DRY RUN - No files were actually modified)")


def main():
    # Determine if this is a dry run
    dry_run = '--dry-run' in sys.argv
    
    # Get the current directory
    current_dir = Path.cwd()
    
    print("PyQt5 to PySide6 Conversion Tool")
    print("=" * 60)
    print(f"Running in: {current_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("=" * 60 + "\n")
    
    # Confirm before proceeding (unless dry run)
    if not dry_run:
        response = input("This will modify all Python files in place. Continue? (y/n): ")
        if response.lower() != 'y':
            print("Conversion cancelled.")
            return
    
    # Create and run converter
    converter = PyQt5ToPySide6Converter(dry_run=dry_run)
    converter.process_directory(current_dir)
    converter.print_summary()
    
    # Additional manual checks reminder
    print("\n" + "=" * 60)
    print("POST-CONVERSION CHECKLIST:")
    print("=" * 60)
    print("""
1. Review the High DPI settings in main.py (PySide6 handles this differently)
2. Test matplotlib plotting functionality 
3. Test all signal/slot connections
4. Verify custom mouse event handlers (e.g., ToggleSlider)
5. Test file dialogs and path operations
6. Verify all enum usages compile correctly
7. Run the application and test all major features
    """)


if __name__ == "__main__":
    main()