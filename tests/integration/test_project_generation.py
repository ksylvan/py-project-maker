"""Integration tests for PyHatchery CLI."""

import os
import subprocess
import sys

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
    cmd: list[str] = [sys.executable, "-m", "pyhatchery"] + args

    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    assert process.returncode == expected_returncode, (
        f"Expected return code {expected_returncode}, got {process.returncode}\n"
        f"stdout: {process.stdout}\n"
        f"stderr: {process.stderr}"
    )

    return process.stdout, process.stderr


class TestCliIntegration:
    """Integration tests for the PyHatchery CLI."""

    def teardown_method(self):
        """Clean up any environment variables set during tests."""
        if "PYHATCHERY_DEBUG" in os.environ:
            os.environ.pop("PYHATCHERY_DEBUG")

    def test_new_project_success_non_interactive(self):
        """Test that 'pyhatchery new my_project' with non-interactive mode."""
        project_name = "my_test_project"
        normalized_name = "my-test-project"

        # Use non-interactive mode with all details provided via CLI flags
        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "Integration Test Author",
            "--email",
            "integration@test.com",
            "--github-username",
            "testuser",
            "--description",
            "A project for integration testing.",
            "--license",
            "MIT",
            "--python-version",
            "3.11",
        ]

        # Set environment variable for debug instead of using --debug flag
        os.environ["PYHATCHERY_DEBUG"] = "1"

        stdout, stderr = run_cli_command(args)

        assert f"Creating new project: {normalized_name}" in stdout
        assert "With details:" in stdout
        assert "Integration Test Author" in stdout
        assert "integration@test.com" in stdout
        assert "Derived PyPI slug:" in stderr
        assert "Derived Python package slug:" in stderr

    def test_new_project_missing_required_fields(self):
        """Test that non-interactive mode with missing required fields shows error."""
        stdout, stderr = run_cli_command(
            ["new", "my-project", "--no-interactive"], expected_returncode=1
        )

        assert stdout == ""
        assert (
            "Error: The following required fields are missing in non-interactive mode:"
            in stderr
        )
        assert "author_name" in stderr
        assert "author_email" in stderr

    def test_missing_project_name(self):
        """Test that 'pyhatchery new' without a name shows an error."""
        stdout, stderr = run_cli_command(["new"], expected_returncode=2)

        assert stdout == ""
        assert "error: the following arguments are required: project_name" in stderr

    def test_invalid_project_name(self):
        """Test that 'pyhatchery new' with an invalid name shows an error and exits."""
        stdout, stderr = run_cli_command(["new", "invalid!name"], expected_returncode=1)

        assert stdout == ""
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
