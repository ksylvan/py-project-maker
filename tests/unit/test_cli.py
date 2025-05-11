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

    # Test for original success case, now needs mocks for new validation steps
    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="mocked-pypi-slug")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="mocked_python_slug"
    )
    @patch(
        "pyhatchery.cli.check_pypi_availability", return_value=(False, None)
    )  # Available, no error
    @patch(
        "pyhatchery.cli.is_valid_python_package_name", return_value=(True, None)
    )  # Valid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_success_no_warnings(
        self,
        mock_is_valid_python_slug: MagicMock,
        mock_check_pypi: MagicMock,
        mock_derive_python_slug: MagicMock,
        mock_normalize: MagicMock,
        mock_pep503_ok: MagicMock,
    ):
        """Test `pyhatchery new project_name` succeeds with no warnings."""
        project_name = "my_new_project"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        expected_stdout = f"Creating new project: {project_name}\n"
        # Stderr will contain the debug prints for slugs
        expected_stderr_part_pypi = "Derived PyPI slug: mocked-pypi-slug"
        expected_stderr_part_python = "Derived Python package slug: mocked_python_slug"

        assert stdout == expected_stdout
        assert expected_stderr_part_pypi in stderr
        assert expected_stderr_part_python in stderr
        # Check that no *warning* messages are in stderr
        assert "Warning:" not in stderr
        assert exit_code == 0
        mock_pep503_ok.assert_called_once_with(project_name)
        mock_normalize.assert_called_once_with(project_name)
        mock_derive_python_slug.assert_called_once_with(project_name)
        mock_check_pypi.assert_called_once_with("mocked-pypi-slug")
        mock_is_valid_python_slug.assert_called_once_with("mocked_python_slug")

    def test_new_project_no_name_ac2(self):
        """AC2: `pyhatchery new` without project name displays error and help."""
        # Argparse handles missing required arguments by printing to stderr and exiting.
        # The exit code for argparse error is typically 2.
        stdout, stderr, exit_code, mock_exit = run_cli_capture_output(["new"])

        assert (
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )  # depending on argparse version/setup
        assert "error: the following arguments are required: project_name" in stderr
        assert stdout == ""
        assert exit_code == 2  # Argparse exits with 2 on argument errors
        mock_exit.assert_called_once_with(2)

    def test_new_project_empty_name_string_ac3(self):
        """AC3: Invalid project names (empty string) result in an error."""
        # Argparse might catch this, or our explicit check might.
        # If argparse catches it as a missing argument
        # (if it treats "" as missing), exit code 2.
        # If our code catches it, exit code 1.
        # Let's assume our code's explicit check for an empty string is not hit
        # because argparse might not allow an empty string for a positional
        # argument if it's not quoted.
        # However, if it *is* passed as `pyhatchery new ""`,
        # then our code should catch it.
        # The current cli.py has `if not args.project_name:`,
        # which would catch an empty string.

        # Test with an explicitly empty string argument
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", ""])

        assert "Error: Project name cannot be empty." in stderr
        assert (
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )
        assert stdout == ""
        assert exit_code == 1
        # mock_exit is not called here because main() returns directly

    @patch(
        "pyhatchery.cli.pep503_name_ok",
        return_value=(False, "Initial name format error."),
    )
    @patch("pyhatchery.cli.pep503_normalize", return_value="pypi-slug")
    @patch("pyhatchery.cli.derive_python_package_slug", return_value="python_slug")
    @patch(
        "pyhatchery.cli.check_pypi_availability", return_value=(False, None)
    )  # Available
    @patch(
        "pyhatchery.cli.is_valid_python_package_name", return_value=(True, None)
    )  # Valid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_initial_name_invalid_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        mock_pep503_ok: MagicMock,
    ):
        """Test warning for initial project name format, but still proceeds."""
        invalid_name = (
            "Invalid_Project_Name_Caps"  # Example that might fail pep503_name_ok
        )
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", invalid_name])

        assert f"Creating new project: {invalid_name}" in stdout
        assert (
            f"Warning: Project name '{invalid_name}': Initial name format error."
            in stderr
        )
        assert "Derived PyPI slug: pypi-slug" in stderr
        assert "Derived Python package slug: python_slug" in stderr
        assert exit_code == 0
        mock_pep503_ok.assert_called_once_with(invalid_name)

    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="taken-pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="valid_python_slug"
    )
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(True, None))  # Taken
    @patch(
        "pyhatchery.cli.is_valid_python_package_name", return_value=(True, None)
    )  # Valid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_pypi_name_taken_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,  # Decorator sets behavior, key to test
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
    ):
        """Test warning if PyPI name is taken."""
        project_name = "someproject"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {project_name}" in stdout
        assert (
            "Warning: The name 'taken-pypi-name' might already be taken on PyPI."
            in stderr
        )
        assert exit_code == 0

    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="valid_python_slug"
    )
    @patch(
        "pyhatchery.cli.check_pypi_availability",
        return_value=(None, "Network error during PyPI check"),
    )  # Check failed
    @patch(
        "pyhatchery.cli.is_valid_python_package_name", return_value=(True, None)
    )  # Valid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_pypi_check_fails_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,  # This mock's behavior is set by the decorator
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
    ):
        """Test warning if PyPI availability check fails."""
        project_name = "someproject"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {project_name}" in stdout
        expected_warning = (
            "Warning: PyPI availability check for 'pypi-name' failed: "
            "Network error during PyPI check"
        )
        assert expected_warning in stderr
        assert exit_code == 0

    @patch("pyhatchery.cli.pep503_name_ok", return_value=(True, None))
    @patch("pyhatchery.cli.pep503_normalize", return_value="pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="Invalid_Python_Slug"
    )
    @patch(
        "pyhatchery.cli.check_pypi_availability", return_value=(False, None)
    )  # Available
    @patch(
        "pyhatchery.cli.is_valid_python_package_name",
        return_value=(False, "Not PEP 8 compliant error message."),
    )  # Invalid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_invalid_python_slug_warning(
        self,
        _mock_is_valid_python_slug: MagicMock,  # Decorator sets behavior
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
    ):
        """Test warning if derived Python package slug is not PEP 8 compliant."""
        project_name = "SomeProjectWithCaps"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {project_name}" in stdout
        expected_warning = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'SomeProjectWithCaps') is not PEP 8 compliant: "
            "Not PEP 8 compliant error message."
        )
        assert expected_warning in stderr
        assert exit_code == 0

    @patch(
        "pyhatchery.cli.pep503_name_ok", return_value=(False, "Initial name problem.")
    )
    @patch("pyhatchery.cli.pep503_normalize", return_value="taken-pypi-name")
    @patch(
        "pyhatchery.cli.derive_python_package_slug", return_value="Invalid_Python_Slug"
    )
    @patch("pyhatchery.cli.check_pypi_availability", return_value=(True, None))  # Taken
    @patch(
        "pyhatchery.cli.is_valid_python_package_name",
        return_value=(False, "Python slug invalid message."),
    )  # Invalid
    # pylint: disable=too-many-arguments, too-many-positional-arguments
    def test_new_project_all_warnings_and_proceeds(
        self,
        _mock_is_valid_python_slug: MagicMock,
        _mock_check_pypi: MagicMock,
        _mock_derive_python_slug: MagicMock,
        _mock_normalize: MagicMock,
        _mock_pep503_ok: MagicMock,
    ):
        """Test CLI proceeds with exit code 0 for all warnings."""
        project_name = "ProblematicName"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {project_name}" in stdout
        assert (
            f"Warning: Project name '{project_name}': Initial name problem." in stderr
        )
        assert (
            "Warning: The name 'taken-pypi-name' might already be taken on PyPI."
            in stderr
        )
        expected_warning_python_slug = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'ProblematicName') is not PEP 8 compliant: "
            "Python slug invalid message."
        )
        assert expected_warning_python_slug in stderr
        assert "Derived PyPI slug: taken-pypi-name" in stderr
        assert "Derived Python package slug: Invalid_Python_Slug" in stderr
        assert exit_code == 0

    def test_no_command_provided(self):
        """Test that running `pyhatchery` without a command shows help."""
        stdout, stderr, exit_code, _ = run_cli_capture_output([])

        assert "PyHatchery: A Python project scaffolding tool." in stderr  # Description
        assert "Commands:" in stderr
        assert "new" in stderr  # 'new' command should be listed
        assert stdout == ""
        assert exit_code == 1  # Our cli.py returns 1 if command is None
        # mock_exit is not called here because main() returns directly
