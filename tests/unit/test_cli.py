"""Unit tests for the PyHatchery CLI."""

import io
from unittest.mock import MagicMock, patch

from pyhatchery.cli import main

# To capture stdout/stderr, argparse's behavior of calling sys.exit directly
# needs to be handled. We can patch sys.exit.


def run_cli_capture_output(args_list: list[str]):
    """
    Helper function to run the CLI main function and capture its output and exit status.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code: int | None = 0  # Default to success

    mock_exit = MagicMock()

    def side_effect_exit(code: int | None):
        nonlocal exit_code
        exit_code = code
        # Raise an exception to stop execution like sys.exit would
        raise SystemExit(code if code is not None else 0)  # SystemExit expects an arg

    mock_exit.side_effect = side_effect_exit

    with (
        patch("sys.stdout", new=stdout_capture),
        patch("sys.stderr", new=stderr_capture),
        patch("sys.exit", new=mock_exit),
    ):
        returned_code: int | None = None
        try:
            # Call the main function from cli.py
            # Note: cli.main expects sys.argv[1:], so we pass the args directly
            returned_code = main(args_list)
            # If main returns without sys.exit being called (by argparse or explicitly),
            # our mock_exit won't be triggered. So, we use the returned code.
            if not mock_exit.called:
                exit_code = returned_code
        except SystemExit as e:
            # This is expected when argparse exits (e.g. for --help or error)
            # or when our mock_exit is called (which sets exit_code via side_effect).
            # If argparse exits directly (mock_exit not called), use e.code.
            if not mock_exit.called:
                exit_code = e.code if isinstance(e.code, int) else 1

    return stdout_capture.getvalue(), stderr_capture.getvalue(), exit_code, mock_exit


class TestCli:
    """Tests for CLI interactions."""

    @patch("pyhatchery.cli.collect_project_details")  # Mock the interactive wizard
    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="my-new-project")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="mocked_python_slug"
    )
    @patch(
        "pyhatchery.cli.check_pypi_availability", return_value=(False, None)
    )  # Available, no error
    @patch(
        "pyhatchery.cli.is_valid_python_package_name", return_value=(True, None)
    )  # Valid
    # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals
    def test_new_project_success_no_warnings(
        self,
        mock_is_valid_python_slug: MagicMock,
        mock_check_pypi: MagicMock,
        mock_derive_python_slug: MagicMock,
        mock_normalize: MagicMock,
        mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test `pyhatchery new project_name` succeeds with no warnings."""
        project_name = "my-new-project"  # Already normalized
        normalized_name = project_name

        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        expected_stdout_creating = f"Creating new project: {normalized_name}\n"
        expected_stdout_details = "With details: {'author_name': 'Test Author'}\n"
        assert expected_stdout_creating in stdout
        assert expected_stdout_details in stdout

        expected_stderr_part_pypi = "Derived PyPI slug: my-new-project"
        expected_stderr_part_python = "Derived Python package slug: mocked_python_slug"
        assert expected_stderr_part_pypi in stderr
        assert expected_stderr_part_python in stderr
        assert "Warning:" not in stderr  # Check for absence of general warnings
        assert exit_code == 0
        mock_pep503_ok.assert_called_once_with(project_name)
        mock_normalize.assert_called_once_with(project_name)
        mock_derive_python_slug.assert_called_once_with(normalized_name)
        mock_check_pypi.assert_called_once_with(normalized_name)
        mock_is_valid_python_slug.assert_called_once_with("mocked_python_slug")
        mock_collect_details.assert_called_once_with(normalized_name, [])

    def test_new_project_no_name_ac2(self):
        """Test `pyhatchery new` without project name displays error and help (AC2)."""
        stdout, stderr, exit_code, mock_exit = run_cli_capture_output(["new"])
        assert (
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )
        assert "error: the following arguments are required: project_name" in stderr
        assert stdout == ""
        assert exit_code == 2
        mock_exit.assert_called_once_with(2)

    def test_new_project_empty_name_string_ac3(self):
        """Test `pyhatchery new ""` (empty project name) results in an error (AC3)."""
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", ""])
        assert "Error: Project name cannot be empty." in stderr
        assert (
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )
        assert stdout == ""
        assert exit_code == 1

    @patch("pyhatchery.cli.collect_project_details")
    @patch(
        "pyhatchery.cli.pep503_name_ok",
        return_value=(False, "Initial name format error."),
    )
    @patch("pyhatchery.cli.pep503_normalize", return_value="pypi-slug")
    @patch("pyhatchery.cli.derive_python_package_slug", return_value="python_slug")
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(False, None))
    @patch("pyhatchery.cli.is_valid_python_package_name", return_value=(True, None))
    def test_new_project_initial_name_invalid_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test warning for initial project name format error."""
        invalid_name = "Invalid_Project_Name_Caps"
        normalized_name_mock = "pypi-slug"
        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", invalid_name])

        assert f"Creating new project: {normalized_name_mock}" in stdout
        assert "With details: {'author_name': 'Test Author'}" in stdout
        assert (
            f"Warning: Project name '{invalid_name}': Initial name format error."
            in stderr
        )
        assert "Derived PyPI slug: pypi-slug" in stderr
        assert "Derived Python package slug: python_slug" in stderr
        assert exit_code == 0
        mock_pep503_ok.assert_called_once_with(invalid_name)
        mock_collect_details.assert_called_once_with(normalized_name_mock, [])

    @patch("pyhatchery.cli.collect_project_details")
    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="taken-pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="valid_python_slug"
    )
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(True, None))  # Taken
    @patch("pyhatchery.cli.is_valid_python_package_name", return_value=(True, None))
    def test_new_project_pypi_name_taken_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test warning when derived PyPI name is likely taken."""
        project_name = "someproject"
        normalized_name_mock = "taken-pypi-name"
        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {normalized_name_mock}" in stdout
        assert "With details: {'author_name': 'Test Author'}" in stdout
        assert (
            "Warning: The name 'taken-pypi-name' might already be taken on PyPI."
            in stderr
        )
        assert exit_code == 0
        expected_warnings = [
            "The name 'taken-pypi-name' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        ]
        mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    @patch("pyhatchery.cli.collect_project_details")
    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="valid_python_slug"
    )
    @patch(
        "pyhatchery.cli.check_pypi_availability",
        return_value=(None, "Network error during PyPI check"),
    )
    @patch("pyhatchery.cli.is_valid_python_package_name", return_value=(True, None))
    def test_new_project_pypi_check_fails_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test warning when PyPI availability check fails."""
        project_name = "someproject"
        normalized_name_mock = "pypi-name"
        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {normalized_name_mock}" in stdout
        assert "With details: {'author_name': 'Test Author'}" in stdout
        expected_warning_msg = (
            "Warning: PyPI availability check for 'pypi-name' failed: "
            "Network error during PyPI check"
        )
        assert expected_warning_msg in stderr
        assert exit_code == 0
        expected_warnings = [
            "PyPI availability check for 'pypi-name' failed: "
            "Network error during PyPI check"
        ]
        mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    @patch("pyhatchery.cli.collect_project_details")
    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="someprojectwithcaps")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="Invalid_Python_Slug"
    )
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(False, None))
    @patch(
        "pyhatchery.cli.is_valid_python_package_name",
        return_value=(False, "Not PEP 8 compliant."),  # Shortened
    )
    def test_new_project_invalid_python_slug_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test warning when derived Python package slug is not PEP 8 compliant."""
        project_name = "SomeProjectWithCaps"
        normalized_name_mock = "someprojectwithcaps"
        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {normalized_name_mock}" in stdout
        assert "With details: {'author_name': 'Test Author'}" in stdout
        expected_warning_msg = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'someprojectwithcaps') is not PEP 8 compliant: "
            "Not PEP 8 compliant."  # Shortened
        )
        assert expected_warning_msg in stderr
        assert exit_code == 0
        expected_warnings = [
            "Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'someprojectwithcaps') is not PEP 8 compliant: "
            "Not PEP 8 compliant."  # Shortened
        ]
        mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    @patch("pyhatchery.cli.collect_project_details")
    @patch(
        "pyhatchery.cli.pep503_name_ok", return_value=(False, "Initial name problem.")
    )
    @patch("pyhatchery.cli.pep503_normalize", return_value="problematicname")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="Invalid_Python_Slug"
    )
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(True, None))  # Taken
    @patch(
        "pyhatchery.cli.is_valid_python_package_name",
        return_value=(False, "Python slug invalid."),  # Shortened
    )
    def test_new_project_all_warnings_and_proceeds(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
        mock_collect_details: MagicMock,
    ):
        """Test CLI proceeds correctly when multiple warnings are present."""
        project_name = "ProblematicName"
        normalized_name_mock = "problematicname"
        mock_collect_details.return_value = {"author_name": "Test Author"}
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {normalized_name_mock}" in stdout
        assert "With details: {'author_name': 'Test Author'}" in stdout
        assert (
            f"Warning: Project name '{project_name}': Initial name problem." in stderr
        )
        assert (
            "Warning: The name 'problematicname' might already be taken on PyPI."
            in stderr
        )
        expected_warning_python_slug_msg = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'problematicname') is not PEP 8 compliant: "
            "Python slug invalid."  # Shortened
        )
        assert expected_warning_python_slug_msg in stderr
        assert "Derived PyPI slug: problematicname" in stderr
        assert "Derived Python package slug: Invalid_Python_Slug" in stderr
        assert exit_code == 0
        expected_warnings_list = [
            "The name 'problematicname' might already be taken on PyPI. "  # Shortened
            "You may want to choose a different name if you plan to publish "
            "this package publicly.",
            "Derived Python package name 'Invalid_Python_Slug' "  # Shortened
            "(from input 'problematicname') is not PEP 8 compliant: "
            "Python slug invalid.",
        ]
        mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings_list
        )

    def test_no_command_provided(self):
        """Test `pyhatchery` without a command shows help and exits."""
        stdout, stderr, exit_code, _ = run_cli_capture_output([])
        assert "PyHatchery: A Python project scaffolding tool." in stderr
        assert "Commands:" in stderr
        assert "new" in stderr
        assert stdout == ""
        assert exit_code == 1
