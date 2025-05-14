"""
Common testing utilities and fixtures for PyHatchery tests.

This module contains shared helper functions and constants used across test files
to reduce code duplication and make tests more maintainable.
"""

import subprocess
import sys
from pathlib import Path

# Helper to get the pyhatchery executable
# This is used in end-to-end tests to run the CLI as a subprocess
PYHATCHERY_CMD = [sys.executable, "-m", "pyhatchery"]


def run_pyhatchery_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """
    Helper function to run pyhatchery CLI commands as a subprocess.

    Args:
        args: List of command-line arguments to pass to pyhatchery
        cwd: Working directory to run the command in, or None to use current directory

    Returns:
        CompletedProcess instance with stdout, stderr, and returncode
    """
    command = PYHATCHERY_CMD + args
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=cwd)


# Define common CLI arguments used across tests to avoid duplication
def get_minimal_non_interactive_args(project_name: str) -> list[str]:
    """
    Returns minimal set of arguments needed for non-interactive project creation.

    Args:
        project_name: The name of the project to create

    Returns:
        List of command-line arguments for non-interactive mode with minimal options
    """
    return [
        "new",
        project_name,
        "--no-interactive",
        "--author",
        "Test Author",
        "--email",
        "test@example.com",
        # Add other necessary defaults if the CLI requires them
        # to pass initial validation
        "--license",
        "MIT",
        "--python-version",
        "3.11",
    ]


def get_full_non_interactive_args(project_name: str) -> list[str]:
    """
    Returns complete set of arguments for non-interactive project creation.

    Args:
        project_name: The name of the project to create

    Returns:
        List of command-line arguments for non-interactive mode with all options
    """
    return [
        "new",
        project_name,
        "--no-interactive",
        "--author",
        "Full Test Author",
        "--email",
        "full_test@example.com",
        "--github-username",
        "fulltester",
        "--description",
        "A full test project.",
        "--license",
        "Apache-2.0",
        "--python-version",
        "3.10",
    ]


def get_sample_project_dir_args(project_name: str, output_dir: Path) -> list[str]:
    """
    Returns the path to the sample project directory.
    Args:
        project_name: The name of the project to create
        output_dir: The directory where the project will be created

    Returns:
        List of command-line arguments for non-interactive mode with --output-dir option
    """
    return [
        "new",
        project_name,
        "--output-dir",
        str(output_dir),
        "--no-interactive",
        "--author",
        "Test Author",
        "--email",
        "test@example.com",
    ]
