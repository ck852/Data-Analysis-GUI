"""
PatchBatch Electrophysiology Data Analysis Tool
Author: Charles Kissell, Northeastern University
License: MIT (see LICENSE file for details)
"""

import os
import sys


class Environment:
    """
    Utility class for detecting runtime environment characteristics.

    Provides static methods to determine if the application is running in a CI (Continuous Integration) environment or in headless mode (no display available).
    """

    @staticmethod
    def is_ci():
        """
        Detect if the application is running in a Continuous Integration (CI) environment.

        Checks for common CI environment variables and absence of display (on non-Windows platforms).

        Returns:
            bool: True if running in CI, False otherwise.
        """
        return any(
            [
                os.environ.get("CI"),
                os.environ.get("GITHUB_ACTIONS"),
                os.environ.get("JENKINS_HOME"),
                not os.environ.get("DISPLAY") and sys.platform != "win32",
            ]
        )

    @staticmethod
    def is_headless():
        """
        Determine if the application is running in headless mode (no graphical display available).

        Returns True if running in CI or if the DISPLAY environment variable is not set.

        Returns:
            bool: True if running headless, False otherwise.
        """
        return Environment.is_ci() or not os.environ.get("DISPLAY")
