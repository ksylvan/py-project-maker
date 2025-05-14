"""
Unit tests for the PyHatchery CLI (Click version).
These tests use click.testing.CliRunner.
"""

from pathlib import Path
from unittest import mock

import click
import pytest
from click.testing import CliRunner

from pyhatchery import __version__
from pyhatchery.cli import (
    ProjectNameDetails,
    check_name_validity,
    create_project,
)
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

    @mock.patch("pyhatchery.cli.create_base_structure")
    @mock.patch("pyhatchery.cli.collect_project_details")
    @mock.patch("pyhatchery.cli.setup_project_directory")  # Added this mock
    def test_debug_flag(
        self,
        mock_setup_dir: mock.MagicMock,  # Added this mock
        mock_collect_details: mock.MagicMock,
        mock_create_structure: mock.MagicMock,
        runner: CliRunner,
        tmp_path: Path,  # Added tmp_path for a unique project dir
    ):
        """Test the --debug flag sets context and is used by subcommands."""
        mock_collect_details.return_value = {
            "author_name": "Debug Author",
            "author_email": "debug@example.com",
            "github_username": "debug_user",
            "project_description": "A debug project.",
            "license": "MIT",
            "python_version_preference": "3.11",
        }
        # Ensure setup_project_directory is mocked to prevent actual dir creation
        # and to return a predictable path for create_base_structure.
        project_name = f"testdebug_{tmp_path.name}"  # Unique project name
        fake_project_path = tmp_path / project_name
        mock_setup_dir.return_value = fake_project_path
        # mock_create_structure.return_value not strictly needed if checking calls

        result = runner.invoke(
            pyhatchery_cli, ["--debug", "new", project_name], prog_name="pyhatchery"
        )

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "'name_for_processing': 'testdebug-test-debug-flag0'" in result.output
        assert "'author_name': 'Debug Author'" in result.output
        mock_collect_details.assert_called_once()
        mock_setup_dir.assert_called_once_with(Path.cwd(), project_name)
        mock_create_structure.assert_called_once_with(
            fake_project_path, project_name, project_name
        )

    @mock.patch("pyhatchery.cli.create_base_structure")  # Added mock
    @mock.patch("pyhatchery.cli.setup_project_directory")  # Added mock
    def test_invalid_pyhatchery_debug_env_var(
        self,
        mock_setup_dir: mock.MagicMock,  # Added mock
        mock_create_structure: mock.MagicMock,  # Added mock
        runner: CliRunner,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,  # Added tmp_path
    ):
        """Test warning when PYHATCHERY_DEBUG env var is invalid."""
        monkeypatch.setenv("PYHATCHERY_DEBUG", "notabool")
        project_name = f"testenvdebug_{tmp_path.name}"  # Unique project name
        fake_project_path = tmp_path / project_name
        mock_setup_dir.return_value = fake_project_path

        with mock.patch("pyhatchery.cli.collect_project_details") as mock_collect:
            mock_collect.return_value = {
                "author_name": "Test",
                "author_email": "test@example.com",
                "license": "MIT",
                "python_version_preference": "3.11",
                "github_username": "",
                "project_description": "",
            }
            # mock_create_structure is already patched at the method level
            # mock_setup_dir is already patched at the method level
            result = runner.invoke(
                pyhatchery_cli, ["new", project_name], prog_name="pyhatchery"
            )

        assert result.exit_code == 0
        assert (
            "Warning: Invalid value for PYHATCHERY_DEBUG environment variable."
            in result.output
        )
        assert "With details:" not in result.output


class TestNewCommand:
    """Tests for the 'new' command logic."""

    @mock.patch("pyhatchery.cli.create_base_structure")
    @mock.patch("pyhatchery.cli.collect_project_details")
    @mock.patch("pyhatchery.cli.check_name_validity")
    @mock.patch("pyhatchery.cli.setup_project_directory")
    def test_new_interactive_mode_success(
        self,
        mock_setup_dir: mock.MagicMock,
        mock_name_checks: mock.MagicMock,
        mock_collect_details: mock.MagicMock,
        mock_create_structure: mock.MagicMock,
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
        mock_setup_dir.return_value = Path("/fake/path/my_interactive_project")

        project_name = "my_interactive_project"
        result = runner.invoke(pyhatchery_cli, ["new", project_name])

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "Creating new project: my-interactive-project" in result.output
        mock_name_checks.assert_called_once_with(
            project_name, "my-interactive-project", "my_interactive_project"
        )
        mock_collect_details.assert_called_once_with("my-interactive-project", [], {})
        mock_setup_dir.assert_called_once()
        args, _ = mock_setup_dir.call_args
        assert args[0] == Path.cwd()
        assert args[1] == project_name
        mock_create_structure.assert_called_once_with(
            Path("/fake/path/my_interactive_project"),
            "my_interactive_project",
            project_name,
        )

    @mock.patch("pyhatchery.cli.create_base_structure")
    @mock.patch("pyhatchery.cli.load_from_env")
    @mock.patch("pyhatchery.cli.check_name_validity")
    @mock.patch("pyhatchery.cli.setup_project_directory")
    def test_new_non_interactive_mode_all_flags(
        self,
        mock_setup_dir: mock.MagicMock,
        mock_name_checks: mock.MagicMock,
        mock_load_env: mock.MagicMock,
        mock_create_structure: mock.MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ):
        """Test `pyhatchery new <name> --no-interactive` with all flags."""
        mock_name_checks.return_value = []
        mock_load_env.return_value = {}
        custom_output_path = tmp_path / "custom_out"
        expected_project_path = custom_output_path / "my_non_interactive_project"
        mock_setup_dir.return_value = expected_project_path

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
            "-o",
            str(custom_output_path),
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 0, f"Output: {result.output}"
        assert "Creating new project: my-non-interactive-project" in result.output
        mock_name_checks.assert_called_once_with(
            project_name,
            "my-non-interactive-project",
            "my_non_interactive_project",
        )
        mock_load_env.assert_called_once()
        mock_setup_dir.assert_called_once_with(custom_output_path, project_name)
        mock_create_structure.assert_called_once_with(
            expected_project_path, "my_non_interactive_project", project_name
        )

    @mock.patch("pyhatchery.cli.create_project")
    @mock.patch("pyhatchery.cli.get_project_details")
    @mock.patch("pyhatchery.cli.validate_project_name")
    def test_new_command_with_output_dir_short_flag(
        self,
        mock_validate_name: mock.MagicMock,
        mock_get_details: mock.MagicMock,
        mock_create_project_func: mock.MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ):
        """Test `pyhatchery new <name> -o <dir>`."""
        project_name = "output_dir_project_short"
        custom_output_dir = tmp_path / "custom_out_short"

        name_data = ProjectNameDetails(
            original_arg=project_name,
            pypi_slug="output-dir-project-short",
            python_slug="output_dir_project_short",
            name_warnings=[],
        )
        mock_validate_name.return_value = name_data
        mock_get_details.return_value = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
        }
        mock_create_project_func.return_value = 0

        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "Test",
            "--email",
            "test@example.com",
            "-o",
            str(custom_output_dir),
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 0, f"Output: {result.output}"
        mock_create_project_func.assert_called_once()
        call_args = mock_create_project_func.call_args[0]
        assert call_args[0] == name_data
        assert call_args[1] == mock_get_details.return_value
        assert call_args[2] == custom_output_dir
        assert call_args[3] is False

    @mock.patch("pyhatchery.cli.create_project")
    @mock.patch("pyhatchery.cli.get_project_details")
    @mock.patch("pyhatchery.cli.validate_project_name")
    def test_new_command_with_output_dir_long_flag(
        self,
        mock_validate_name: mock.MagicMock,
        mock_get_details: mock.MagicMock,
        mock_create_project_func: mock.MagicMock,
        runner: CliRunner,
        tmp_path: Path,
    ):
        """Test `pyhatchery new <name> --output-dir <dir>`."""
        project_name = "output_dir_project_long"
        custom_output_dir = tmp_path / "custom_out_long"

        name_data = ProjectNameDetails(
            original_arg=project_name,
            pypi_slug="output-dir-project-long",
            python_slug="output_dir_project_long",
            name_warnings=[],
        )
        mock_validate_name.return_value = name_data
        mock_get_details.return_value = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
        }
        mock_create_project_func.return_value = 0

        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "Test",
            "--email",
            "test@example.com",
            "--output-dir",
            str(custom_output_dir),
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 0, f"Output: {result.output}"
        mock_create_project_func.assert_called_once()
        call_args = mock_create_project_func.call_args[0]
        assert call_args[2] == custom_output_dir

    @mock.patch("pyhatchery.cli.create_project")
    @mock.patch("pyhatchery.cli.get_project_details")
    @mock.patch("pyhatchery.cli.validate_project_name")
    def test_new_command_without_output_dir_uses_cwd(
        self,
        mock_validate_name: mock.MagicMock,
        mock_get_details: mock.MagicMock,
        mock_create_project_func: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test `pyhatchery new <name>` uses None for output_dir by default."""
        project_name = "default_output_dir_project"
        name_data = ProjectNameDetails(
            original_arg=project_name,
            pypi_slug="default-output-dir-project",
            python_slug="default_output_dir_project",
            name_warnings=[],
        )
        mock_validate_name.return_value = name_data
        mock_get_details.return_value = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
        }
        mock_create_project_func.return_value = 0

        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "Test",
            "--email",
            "test@example.com",
        ]
        result = runner.invoke(pyhatchery_cli, args)

        assert result.exit_code == 0, f"Output: {result.output}"
        mock_create_project_func.assert_called_once()
        call_args = mock_create_project_func.call_args[0]
        assert call_args[2] is None

    @mock.patch("pyhatchery.cli.setup_project_directory")
    @mock.patch("pyhatchery.cli.create_base_structure")
    def test_create_project_file_exists_error(
        self,
        mock_create_base_structure: mock.MagicMock,
        mock_setup_project_directory: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test FileExistsError handling in create_project."""
        _ = runner
        mock_setup_project_directory.side_effect = FileExistsError(
            "Directory already exists"
        )

        name_data = ProjectNameDetails(
            original_arg="test_project",
            pypi_slug="test-project",
            python_slug="test_project",
            name_warnings=[],
        )
        project_details = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "project_name_original": "test_project",
            "python_package_slug": "test_project",
        }

        result_code = create_project(
            name_data, project_details, output_dir=None, debug=False
        )

        assert result_code == 1
        mock_setup_project_directory.assert_called_once_with(Path.cwd(), "test_project")
        mock_create_base_structure.assert_not_called()

    @mock.patch("pyhatchery.cli.setup_project_directory")
    @mock.patch("pyhatchery.cli.create_base_structure")
    def test_create_project_os_error_from_setup(
        self,
        mock_create_base_structure: mock.MagicMock,
        mock_setup_project_directory: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test OSError from setup_project_directory in create_project."""
        _ = runner
        mock_setup_project_directory.side_effect = OSError(
            "Permission denied during setup"
        )

        name_data = ProjectNameDetails(
            original_arg="test_os_error_setup",
            pypi_slug="test-os-error-setup",
            python_slug="test_os_error_setup",
            name_warnings=[],
        )
        project_details = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "project_name_original": "test_os_error_setup",
            "python_package_slug": "test_os_error_setup",
        }
        custom_output = Path("/custom/output/dir")
        result_code = create_project(
            name_data, project_details, output_dir=custom_output, debug=False
        )

        assert result_code == 1
        mock_setup_project_directory.assert_called_once_with(
            custom_output, "test_os_error_setup"
        )
        mock_create_base_structure.assert_not_called()

    @mock.patch("pyhatchery.cli.setup_project_directory")
    @mock.patch("pyhatchery.cli.create_base_structure")
    def test_create_project_os_error_from_create_base(
        self,
        mock_create_base_structure: mock.MagicMock,
        mock_setup_project_directory: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test OSError from create_base_structure in create_project."""
        _ = runner
        fake_project_root = Path("/fake/project/root")
        mock_setup_project_directory.return_value = fake_project_root
        mock_create_base_structure.side_effect = OSError(
            "Permission denied during create_base"
        )

        name_data = ProjectNameDetails(
            original_arg="test_os_error_create",
            pypi_slug="test-os-error-create",
            python_slug="test_os_error_create",
            name_warnings=[],
        )
        project_details = {
            "author_name": "Test Author",
            "author_email": "test@example.com",
            "project_name_original": "test_os_error_create",
            "python_package_slug": "test_os_error_create",
        }

        result_code = create_project(
            name_data, project_details, output_dir=None, debug=False
        )

        assert result_code == 1
        mock_setup_project_directory.assert_called_once_with(
            Path.cwd(), "test_os_error_create"
        )
        mock_create_base_structure.assert_called_once_with(
            fake_project_root, "test_os_error_create", "test_os_error_create"
        )


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


class TestProjectNameValidation:
    """Tests for project name validation logic."""

    @mock.patch("pyhatchery.cli.check_pypi_availability")
    @mock.patch("pyhatchery.cli.is_valid_python_package_name")
    def test_check_name_validity_with_multiple_warnings(
        self,
        mock_is_valid_python_package: mock.MagicMock,
        mock_check_pypi: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test all warning scenarios in check_name_validity."""
        mock_check_pypi.return_value = (True, None)
        mock_is_valid_python_package.return_value = (False, "Not valid")

        _ = runner

        original_name = "test_name"
        pypi_slug = "test-name"
        python_slug = "test_name"

        with mock.patch("pyhatchery.cli.click.secho") as mock_secho:
            warnings = check_name_validity(original_name, pypi_slug, python_slug)

        _ = mock_secho
        assert len(warnings) == 2
        assert any("might already be taken on PyPI" in w for w in warnings)
        assert any("is not PEP 8 compliant" in w for w in warnings)

    @mock.patch("pyhatchery.cli.check_pypi_availability")
    def test_check_name_validity_pypi_error(
        self, mock_check_pypi: mock.MagicMock, runner: CliRunner
    ):
        """Test PyPI check error path in check_name_validity."""
        mock_check_pypi.return_value = (None, "Network error")

        _ = runner

        with mock.patch("pyhatchery.cli.click.secho"):
            warnings = check_name_validity("test_name", "test-name", "test_name")

        assert len(warnings) == 1
        assert "PyPI availability check" in warnings[0]
        assert "failed: Network error" in warnings[0]

    @mock.patch("pyhatchery.cli.get_project_details")
    @mock.patch("pyhatchery.cli.validate_project_name")
    def test_new_command_get_project_details_returns_none(
        self,
        mock_validate_name: mock.MagicMock,
        mock_get_details: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test handling when get_project_details returns None."""
        name_data = ProjectNameDetails(
            original_arg="test_project",
            pypi_slug="test-project",
            python_slug="test_project",
            name_warnings=[],
        )
        mock_validate_name.return_value = name_data
        mock_get_details.return_value = None

        with mock.patch.object(click.Context, "exit") as mock_exit:
            _ = runner.invoke(pyhatchery_cli, ["new", "test_project"])
            mock_exit.assert_any_call(1)

    @mock.patch("pyhatchery.cli.create_project")  # Added this line
    @mock.patch("pyhatchery.cli.validate_project_name")
    @mock.patch("pyhatchery.cli.get_project_details")
    def test_new_command_create_project_returns_error(
        self,
        mock_get_details: mock.MagicMock,
        mock_validate_name: mock.MagicMock,
        mock_create_project: mock.MagicMock,
        runner: CliRunner,
    ):
        """Test handling when create_project returns an error code."""
        name_data = ProjectNameDetails(
            original_arg="test_project",
            pypi_slug="test-project",
            python_slug="test_project",
            name_warnings=[],
        )
        mock_validate_name.return_value = name_data
        mock_get_details.return_value = {
            "author_name": "Test",
            "author_email": "test@example.com",
        }
        mock_create_project.return_value = 1

        with mock.patch.object(click.Context, "exit") as mock_exit:
            _ = runner.invoke(pyhatchery_cli, ["new", "test_project"])
            mock_exit.assert_any_call(1)
