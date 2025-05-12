"""
Unit tests for the PyHatchery CLI (Click version).
These tests use click.testing.CliRunner.
"""

from unittest import mock

import pytest
from click.testing import CliRunner

from pyhatchery import __version__
from pyhatchery.cli import (
    cli as pyhatchery_cli,  # Renamed to avoid conflict with pytest 'cli' fixture
)


@pytest.fixture(name="runner")
def cli_runner() -> CliRunner:
    """Fixture to provide a CliRunner instance."""
    return CliRunner()


class TestBasicFunctionality:
    """Tests for basic CLI functionality like version and help."""

    def test_version_short_flag(self, runner: CliRunner):
        """Test `pyhatchery -v`."""
        result = runner.invoke(pyhatchery_cli, ["-v"])
        assert result.exit_code == 0
        assert f"pyhatchery {__version__}" in result.output
        assert result.exception is None

    def test_version_long_flag(self, runner: CliRunner):
        """Test `pyhatchery --version`."""
        result = runner.invoke(pyhatchery_cli, ["--version"])
        assert result.exit_code == 0
        assert f"pyhatchery {__version__}" in result.output
        assert result.exception is None

    def test_help_short_flag(self, runner: CliRunner):
        """Test `pyhatchery -h`."""
        result = runner.invoke(pyhatchery_cli, ["-h"], prog_name="pyhatchery")
        assert result.exit_code == 0
        assert "Usage: pyhatchery [OPTIONS] COMMAND [ARGS]..." in result.output
        assert "PyHatchery: A Python project scaffolding tool." in result.output
        assert "new" in result.output
        assert result.exception is None

    def test_help_long_flag(self, runner: CliRunner):
        """Test `pyhatchery --help`."""
        result = runner.invoke(pyhatchery_cli, ["--help"], prog_name="pyhatchery")
        assert result.exit_code == 0
        assert "Usage: pyhatchery [OPTIONS] COMMAND [ARGS]..." in result.output
        assert "PyHatchery: A Python project scaffolding tool." in result.output
        assert "new" in result.output
        assert result.exception is None

    def test_new_command_help(self, runner: CliRunner):
        """Test `pyhatchery new --help`."""
        result = runner.invoke(
            pyhatchery_cli, ["new", "--help"], prog_name="pyhatchery"
        )
        assert result.exit_code == 0
        assert "Usage: pyhatchery new [OPTIONS] PROJECT_NAME" in result.output
        assert "Create a new Python project." in result.output
        assert result.exception is None

    @mock.patch("pyhatchery.cli.collect_project_details")
    def test_debug_flag(self, mock_collect_details: mock.MagicMock, runner: CliRunner):
        """Test the --debug flag sets context and is used by subcommands."""
        mock_collect_details.return_value = {
            "author_name": "Debug Author",
            "author_email": "debug@example.com",
            "github_username": "debug_user",
            "project_description": "A debug project.",
            "license": "MIT",
            "python_version_preference": "3.11",
        }
        project_name = "testdebug"
        result = runner.invoke(
            pyhatchery_cli, ["--debug", "new", project_name], prog_name="pyhatchery"
        )

        assert result.exit_code == 0, f"Output: {result.output}"
        assert f"'name_for_processing': '{project_name}'" in result.output
        assert "'author_name': 'Debug Author'" in result.output
        mock_collect_details.assert_called_once()

    def test_invalid_pyhatchery_debug_env_var(
        self, runner: CliRunner, monkeypatch: pytest.MonkeyPatch
    ):
        """Test warning when PYHATCHERY_DEBUG env var is invalid."""
        monkeypatch.setenv("PYHATCHERY_DEBUG", "notabool")
        with mock.patch("pyhatchery.cli.collect_project_details") as mock_collect:
            mock_collect.return_value = {
                "author_name": "Test",
                "author_email": "test@example.com",
                "license": "MIT",
                "python_version_preference": "3.11",
                "github_username": "",
                "project_description": "",
            }
            result = runner.invoke(
                pyhatchery_cli, ["new", "testenvdebug"], prog_name="pyhatchery"
            )

        assert result.exit_code == 0
        assert (
            "Warning: Invalid value for PYHATCHERY_DEBUG environment variable."
            in result.output
        )
        assert "With details:" not in result.output


class TestNewCommand:
    """Tests for the 'new' command logic."""

    @mock.patch("pyhatchery.cli.collect_project_details")
    @mock.patch("pyhatchery.cli._perform_project_name_checks")
    def test_new_interactive_mode_success(
        self,
        mock_name_checks: mock.MagicMock,
        mock_collect_details: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test `pyhatchery new <name>` in interactive mode (mocked)."""
        mock_name_checks.return_value = []
        mock_collect_details.return_value = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "github_username": "testuser",
            "project_description": "A test project.",
            "license": "MIT",
            "python_version_preference": "3.11",
        }
        project_name = "my_interactive_project"
        result = runner.invoke(pyhatchery_cli, ["new", project_name])

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "Creating new project: my-interactive-project" in result.output
        assert "Project generation logic would run here." in result.output
        mock_name_checks.assert_called_once_with(
            project_name, "my-interactive-project", "my_interactive_project"
        )
        mock_collect_details.assert_called_once_with("my-interactive-project", [])

    @mock.patch("pyhatchery.cli.load_from_env")
    @mock.patch("pyhatchery.cli._perform_project_name_checks")
    def test_new_non_interactive_mode_all_flags(
        self,
        mock_name_checks: mock.MagicMock,
        mock_load_env: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test `pyhatchery new <name> --no-interactive` with all flags."""
        mock_name_checks.return_value = []
        mock_load_env.return_value = {}
        project_name = "my_non_interactive_project"
        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "CLI Author",
            "--email",
            "cli@example.com",
            "--github-username",
            "cliuser",
            "--description",
            "CLI project.",
            "--license",
            "Apache-2.0",
            "--python-version",
            "3.10",
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "Creating new project: my-non-interactive-project" in result.output
        assert "Project generation logic would run here." in result.output
        mock_name_checks.assert_called_once_with(
            project_name,
            "my-non-interactive-project",
            "my_non_interactive_project",
        )
        mock_load_env.assert_called_once()

    @mock.patch("pyhatchery.cli.load_from_env")
    @mock.patch("pyhatchery.cli._perform_project_name_checks")
    def test_new_non_interactive_mode_env_override(
        self,
        mock_name_checks: mock.MagicMock,
        mock_load_env: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test CLI flags override .env values in non-interactive mode."""
        mock_name_checks.return_value = []
        mock_load_env.return_value = {
            "AUTHOR_NAME": "Env Author",
            "AUTHOR_EMAIL": "env@example.com",
            "GITHUB_USERNAME": "envuser",
            "PROJECT_DESCRIPTION": "Env project.",
            "LICENSE": "GPL-3.0",
            "PYTHON_VERSION": "3.9",
        }
        project_name = "env_override_project"
        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "CLI Author",
            "--email",
            "cli_override@example.com",
        ]
        result = runner.invoke(pyhatchery_cli, ["--debug"] + args)

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "Creating new project: env-override-project" in result.output
        assert "'author_name': 'CLI Author'" in result.output
        assert "'author_email': 'cli_override@example.com'" in result.output
        assert "'github_username': 'envuser'" in result.output
        assert "'license': 'GPL-3.0'" in result.output
        mock_load_env.assert_called_once()

    @mock.patch("pyhatchery.cli._perform_project_name_checks")
    def test_new_non_interactive_mode_missing_required_flags(
        self, mock_name_checks: mock.MagicMock, runner: CliRunner
    ):
        """Test non-interactive mode fails if required flags are missing."""
        mock_name_checks.return_value = []
        project_name = "missing_flags_project"
        args = [
            "new",
            project_name,
            "--no-interactive",
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 1, f"Output: {result.output}"
        assert "Error: The following required fields are missing" in result.output
        assert "- author_name" in result.output
        assert "- author_email" in result.output

    @mock.patch("pyhatchery.cli.check_pypi_availability")
    @mock.patch("pyhatchery.cli.is_valid_python_package_name")
    def test_new_command_name_warnings_displayed(
        self,
        mock_is_valid_python_package_name: mock.MagicMock,
        mock_check_pypi: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test that project name warnings are displayed."""
        mock_check_pypi.return_value = (True, None)
        mock_is_valid_python_package_name.return_value = (
            False,
            "Is not valid.",
        )

        project_name = "WarningProject"
        result = runner.invoke(
            pyhatchery_cli,
            [
                "new",
                project_name,
                "--no-interactive",
                "--author",
                "Warn Author",
                "--email",
                "warn@example.com",
            ],
        )

        assert result.exit_code == 0
        assert (
            "Warning: The name 'warningproject' might already be taken on PyPI."
            in result.output
        )
        assert (
            "Warning: Derived Python package name 'warningproject' "
            "(from input 'WarningProject') is not PEP 8 compliant: Is not valid."
            in result.output
        )
        assert "Creating new project: warningproject" in result.output

    @mock.patch("pyhatchery.cli.check_pypi_availability")
    @mock.patch("pyhatchery.cli.is_valid_python_package_name")
    def test_new_command_pypi_check_network_error(
        self,
        mock_is_valid_python_package_name: mock.MagicMock,
        mock_check_pypi: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test that PyPI check network error is handled and warning displayed."""
        mock_check_pypi.return_value = (None, "Simulated Network Error")
        mock_is_valid_python_package_name.return_value = (True, None)

        project_name = "PypiErrorProject"
        result = runner.invoke(
            pyhatchery_cli,
            [
                "new",
                project_name,
                "--no-interactive",
                "--author",
                "PypiErr Author",
                "--email",
                "pyperr@example.com",
            ],
            prog_name="pyhatchery",
        )

        assert result.exit_code == 0
        assert (
            "PyPI availability check for 'pypierrorproject' "
            "failed: Simulated Network Error" in result.output
        )
        assert "Creating new project: pypierrorproject" in result.output


class TestErrorConditions:
    """Tests for CLI error conditions."""

    def test_new_command_no_project_name(self, runner: CliRunner):
        """Test `pyhatchery new` without a project name."""
        result = runner.invoke(pyhatchery_cli, ["new"])
        assert result.exit_code == 2
        assert "Error: Missing argument 'PROJECT_NAME'." in result.output
        assert result.exception is not None

    def test_new_command_invalid_chars_in_project_name(self, runner: CliRunner):
        """Test `pyhatchery new` with invalid characters in project name."""
        result = runner.invoke(pyhatchery_cli, ["new", "invalid!name"])
        assert result.exit_code == 1
        assert "Error: Project name contains invalid characters: '!'" in result.output

    def test_invalid_command(self, runner: CliRunner):
        """Test an invalid command."""
        result = runner.invoke(pyhatchery_cli, ["invalidcommand"])
        assert result.exit_code == 2
        assert "Error: No such command 'invalidcommand'." in result.output
        assert result.exception is not None
