"""Integration tests for PyHatchery CLI."""

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

    def test_new_project_success(self):
        """Test that 'pyhatchery new my_project' works correctly."""
        stdout, stderr = run_cli_command(["new", "my_test_project"])

        assert "Creating new project: my_test_project" in stdout
        assert stderr.startswith("Derived PyPI slug:")

    def test_missing_project_name(self):
        """Test that 'pyhatchery new' without a name shows an error."""
        stdout, stderr = run_cli_command(["new"], expected_returncode=2)

        assert stdout == ""
        assert "error: the following arguments are required: project_name" in stderr

    def test_invalid_project_name(self):
        """Test that 'pyhatchery new' with an invalid name shows an error."""
        stdout, stderr = run_cli_command(["new", "invalid!name"], expected_returncode=1)

        assert stdout == ""
        assert (
            "Error: Project name 'invalid!name' violates PEP 503 conventions." in stderr
        )

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
