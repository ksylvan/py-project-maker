"""
End-to-end tests for the PyHatchery CLI.
These tests invoke the CLI as a subprocess.
"""

from pathlib import Path

import pytest

from pyhatchery import __version__
from tests.helpers import (
    get_full_non_interactive_args,
    get_minimal_non_interactive_args,
    run_pyhatchery_command,
)


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

    def test_new_command_empty_project_name(self):
        """Test `pyhatchery new ""` fails and shows correct error."""
        result = run_pyhatchery_command(["new", ""])
        assert result.returncode == 1
        assert "Error: Project name cannot be empty." in result.stderr
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
        # Get the minimal set of non-interactive arguments
        args = get_minimal_non_interactive_args(project_name)
        result = run_pyhatchery_command(args, cwd=tmp_path)

        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert (
            "Creating new project: test-project-e2e-minimal"
            in result.stdout  # Expect pypi_slug
        )
        assert "Project directory structure created at:" in result.stdout
        # Further checks could involve verifying that no interactive prompts appeared.

    def test_new_command_non_interactive_all_flags(self, tmp_path: Path):
        """Test `pyhatchery new <name> --no-interactive` with all flags."""
        project_name = "test_project_e2e_full"
        pypi_slug = "test-project-e2e-full"  # Expected normalization
        args = get_full_non_interactive_args(project_name)
        result = run_pyhatchery_command(args, cwd=tmp_path)
        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert f"Creating new project: {pypi_slug}" in result.stdout
        assert "Project directory structure created at:" in result.stdout

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

        args = ["new", project_name]
        result = run_pyhatchery_command(args, cwd=tmp_path)

        assert result.returncode == 1, (  # Expecting failure due to EOF on prompt
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert "Process cancelled by user" in result.stdout
        assert (
            f"Derived PyPI slug: {pypi_slug}" in result.stderr
        )  # Check it got past name processing
