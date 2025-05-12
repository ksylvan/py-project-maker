"""
End-to-end tests for the PyHatchery CLI.
These tests invoke the CLI as a subprocess.
"""

import subprocess
import sys
from pathlib import Path

import pytest

from pyhatchery import __version__

# Helper to get the pyhatchery executable
# This might need adjustment based on how the project is structured
# and how it's intended to be run during tests
# (e.g., via `python -m pyhatchery` or a script)
PYHATCHERY_CMD = [sys.executable, "-m", "pyhatchery"]


def run_pyhatchery_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Helper function to run pyhatchery CLI commands."""
    command = PYHATCHERY_CMD + args
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=cwd)


class TestCliEndToEnd:
    """End-to-end tests for CLI functionality."""

    def test_version_short_flag(self):
        """Test `pyhatchery -v` displays the correct version."""
        result = run_pyhatchery_command(["-v"])
        assert result.returncode == 0
        assert f"pyhatchery {__version__}" in result.stdout
        assert result.stderr == ""

    def test_version_long_flag(self):
        """Test `pyhatchery --version` displays the correct version."""
        result = run_pyhatchery_command(["--version"])
        assert result.returncode == 0
        assert f"pyhatchery {__version__}" in result.stdout
        assert result.stderr == ""

    def test_help_short_flag(self):
        """Test `pyhatchery -h` displays help."""
        result = run_pyhatchery_command(["-h"])
        assert result.returncode == 0
        assert (
            "Usage: python -m pyhatchery [OPTIONS] COMMAND [ARGS]..." in result.stdout
        )
        assert "PyHatchery: A Python project scaffolding tool." in result.stdout
        assert "Commands:" in result.stdout
        assert "new" in result.stdout
        assert result.stderr == ""

    def test_help_long_flag(self):
        """Test `pyhatchery --help` displays help."""
        result = run_pyhatchery_command(["--help"])
        assert result.returncode == 0
        assert (
            "Usage: python -m pyhatchery [OPTIONS] COMMAND [ARGS]..." in result.stdout
        )
        assert "PyHatchery: A Python project scaffolding tool." in result.stdout
        assert "Commands:" in result.stdout
        assert "new" in result.stdout
        assert result.stderr == ""

    def test_new_command_help(self):
        """Test `pyhatchery new --help` displays help for the new command."""
        result = run_pyhatchery_command(["new", "--help"])
        assert result.returncode == 0
        assert "Usage: python -m pyhatchery new [OPTIONS] PROJECT_NAME" in result.stdout
        assert "Create a new Python project." in result.stdout
        assert "--no-interactive" in result.stdout
        assert "--author" in result.stdout
        assert result.stderr == ""

    def test_new_command_missing_project_name(self):
        """Test `pyhatchery new` without project_name fails and shows error."""
        result = run_pyhatchery_command(["new"])
        assert result.returncode == 2  # Click's error code for missing argument
        assert "Error: Missing argument 'PROJECT_NAME'." in result.stderr
        assert result.stdout == ""

    def test_new_command_invalid_project_name_chars(self):
        """Test `pyhatchery new` with invalid characters in project_name."""
        # Assuming '!' is an invalid character based on has_invalid_characters
        result = run_pyhatchery_command(["new", "invalid!name"])
        assert result.returncode == 1
        assert "Error: Project name contains invalid characters: '!'" in result.stderr
        assert result.stdout == ""

    def test_new_command_non_interactive_minimal(self, tmp_path: Path):
        """
        Test `pyhatchery new <name> --no-interactive` with minimal required flags.
        This test primarily checks that the command starts and attempts to proceed,
        rather than full project generation which is complex for an E2E CLI test
        without extensive mocking or actual generation.
        """
        project_name = "test_project_e2e_minimal"
        # Assuming author and email are the minimal required for non-interactive
        # and other components (like PyPI check) are mocked or handled gracefully.
        # For this E2E, we're mostly checking CLI parsing and initial flow.
        args = [
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
        result = run_pyhatchery_command(args, cwd=tmp_path)

        # Check for successful start of the process (exit code 0)
        # and some expected output indicating it's proceeding.
        # The actual project generation is mocked out in cli.py for now.
        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (
            "Creating new project: test-project-e2e-minimal"
            in result.stdout  # Expect pypi_slug
        )
        assert "Project generation logic would run here." in result.stdout
        # Further checks could involve verifying that no interactive prompts appeared.

    def test_new_command_non_interactive_all_flags(self, tmp_path: Path):
        """Test `pyhatchery new <name> --no-interactive` with all flags."""
        project_name = "test_project_e2e_full"
        pypi_slug = "test-project-e2e-full"  # Expected normalization
        args = [
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
        result = run_pyhatchery_command(args, cwd=tmp_path)
        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert f"Creating new project: {pypi_slug}" in result.stdout
        assert "Project generation logic would run here." in result.stdout
        # Debug specific assertions removed for focus, covered by unit tests
        # assert (
        #     f"'original_input_name': '{project_name}'" in result.stdout
        # )
        # assert f"'name_for_processing': '{pypi_slug}'" in result.stdout
        # assert "'author_name': 'Full Test Author'" in result.stdout
        # assert "'license': 'Apache-2.0'" in result.stdout

    def test_new_command_interactive_start(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ):
        """
        Test `pyhatchery new <name>` starts the interactive flow.
        We'll mock `collect_project_details` to prevent actual interaction.
        """
        project_name = "interactive_test_project"
        pypi_slug = "interactive-test-project"

        _ = monkeypatch  # To avoid unused variable warning

        # Mock collect_project_details to simulate it being called
        # and returning some dummy data, then exiting.
        # This is tricky for E2E subprocess tests.
        # A better approach for testing "interactive start" might be
        # to check for the initial prompts if we could control stdin/stdout
        # of the subprocess, or rely on unit tests for the wizard itself.

        # For this E2E, we'll check if the non-interactive path is NOT taken
        # and that it attempts to proceed, implying interactive mode was entered.
        # The actual interactive prompts are hard to test via subprocess without PTY.

        # Expect it to pass name checks and attempt to run `collect_project_details`.
        # Since `collect_project_details` isn't mocked at subprocess level,
        # it will try to run. We check for output indicating it passed name checks,
        # implying interactive mode started.

        args = ["new", project_name]
        result = run_pyhatchery_command(args, cwd=tmp_path)

        # If it tries to run interactively and we don't provide input,
        # it might hang or error. The current cli.py mock for generation
        # means it will print "Project generation logic would run here."
        # if collect_project_details returns successfully.
        # For this E2E, if it fails due to prompt EOF, that's an indication
        # it tried interactive.
        # The actual output shows "End of file reached. Exiting." and return code 1.
        assert result.returncode == 1, (  # Expecting failure due to EOF on prompt
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "End of file reached. Exiting." in result.stdout
        assert (
            f"Derived PyPI slug: {pypi_slug}" in result.stderr
        )  # Check it got past name processing
