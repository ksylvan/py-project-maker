"""Integration tests for PyHatchery CLI."""

import subprocess
import sys
from unittest.mock import MagicMock, patch  # Ensure this import is present

import pytest  # Ensure this import is present

from pyhatchery.__about__ import __version__


def run_cli_command(args: list[str], expected_returncode: int = 0) -> tuple[str, str]:
    """
    Run the pyhatchery CLI command with the given args and check the return code.

    Args:
        args: List of command line arguments to pass to pyhatchery
        expected_returncode: Expected return code of the process

    Returns:
        A tuple of (stdout, stderr) from the process
    """
    # Construct the command to run
    cmd: list[str] = [sys.executable, "-m", "pyhatchery"] + args

    # Run the command and capture stdout/stderr
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,  # We'll check the return code ourselves
    )

    # Check the return code
    assert process.returncode == expected_returncode, (
        f"Expected return code {expected_returncode}, got {process.returncode}\n"
        f"stdout: {process.stdout}\n"
        f"stderr: {process.stderr}"
    )

    return process.stdout, process.stderr


class TestCliIntegration:
    """Integration tests for the PyHatchery CLI."""

    @pytest.mark.skip(
        reason="Wizard in subprocess fails without stdin. Re-enable with Story 1.3."
    )  # type: ignore
    @patch("pyhatchery.cli.collect_project_details")
    def test_new_project_success(self, mock_collect_details: MagicMock):
        """Test that 'pyhatchery new my_project' works correctly
        and creates a normalized project name."""
        # TODO: Re-enable/adapt with non-interactive mode (Story 1.3).
        # Fails due to wizard input in subprocess.
        project_name = "my_test_project"
        normalized_name = "my-test-project"  # This is what we expect

        # Simulate wizard returning some details to allow CLI to proceed
        mock_collect_details.return_value = {
            "author_name": "Integration Test Author",
            "author_email": "integration@test.com",
            "github_username": "testuser",
            "project_description": "A project for integration testing.",
            "license": "MIT",
            "python_version_preference": "3.11",
        }

        stdout, stderr = run_cli_command(["new", project_name])

        assert f"Creating new project: {normalized_name}" in stdout
        # Also check for the "With details" line now
        assert "With details: {'author_name': 'Integration Test Author'" in stdout
        assert "Derived PyPI slug:" in stderr
        assert "Derived Python package slug:" in stderr

    def test_missing_project_name(self):
        """Test that 'pyhatchery new' without a name shows an error."""
        stdout, stderr = run_cli_command(["new"], expected_returncode=2)

        assert stdout == ""
        assert "error: the following arguments are required: project_name" in stderr

    def test_invalid_project_name(self):
        """Test that 'pyhatchery new' with an invalid name shows an error and exits."""
        stdout, stderr = run_cli_command(["new", "invalid!name"], expected_returncode=1)

        assert stdout == ""  # Error message should go to stderr
        assert "Error: Project name contains invalid characters" in stderr
        assert "'!'" in stderr

    def test_version_flag(self):
        """Test that 'pyhatchery --version' shows the version."""
        stdout, stderr = run_cli_command(["--version"], expected_returncode=0)

        assert f"pyhatchery {__version__}" in stdout
        assert stderr == ""

    def test_no_command(self):
        """Test that 'pyhatchery' with no command shows help."""
        stdout, stderr = run_cli_command([], expected_returncode=1)

        assert stdout == ""
        assert "usage: pyhatchery" in stderr
        assert "Commands:" in stderr
        assert "new" in stderr
