"""Unit tests for the PyHatchery CLI."""

import io
import os
import unittest
from unittest.mock import MagicMock, patch

from pyhatchery.cli import main


def run_cli_capture_output(args_list: list[str]):
    """
    Helper function to run the CLI main function and capture its output and exit status.
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    exit_code: int | None = 0

    mock_exit = MagicMock()

    def side_effect_exit(code: int | None):
        nonlocal exit_code
        exit_code = code
        raise SystemExit(code if code is not None else 0)

    mock_exit.side_effect = side_effect_exit

    with (
        patch("sys.stdout", new=stdout_capture),
        patch("sys.stderr", new=stderr_capture),
        patch("sys.exit", new=mock_exit),
    ):
        returned_code: int | None = None
        try:
            returned_code = main(args_list)
            if not mock_exit.called:
                exit_code = returned_code
        except SystemExit as e:
            if not mock_exit.called:
                exit_code = e.code if isinstance(e.code, int) else 1

    return stdout_capture.getvalue(), stderr_capture.getvalue(), exit_code, mock_exit


class TestCli(unittest.TestCase):
    """Tests for CLI interactions."""

    def setUp(self):
        """Set up common test mocks."""
        self.mock_collect_details = patch(
            "pyhatchery.cli.collect_project_details"
        ).start()
        self.mock_pep503_ok = patch("pyhatchery.cli.pep503_name_ok").start()
        self.mock_normalize = patch("pyhatchery.cli.pep503_normalize").start()
        self.mock_derive_python_slug = patch(
            "pyhatchery.cli.derive_python_package_slug"
        ).start()
        self.mock_check_pypi = patch("pyhatchery.cli.check_pypi_availability").start()
        self.mock_is_valid_python_name = patch(
            "pyhatchery.cli.is_valid_python_package_name"
        ).start()

        self.mock_pep503_ok.return_value = (True, None)
        self.mock_normalize.return_value = "my-new-project"
        self.mock_derive_python_slug.return_value = "mocked_python_slug"
        self.mock_check_pypi.return_value = (False, None)
        self.mock_is_valid_python_name.return_value = (True, None)
        self.mock_collect_details.return_value = {"author_name": "Test Author"}
        os.environ["PYHATCHERY_DEBUG"] = "1"

    def tearDown(self):
        """Clean up patches."""
        patch.stopall()
        os.environ.pop("PYHATCHERY_DEBUG", None)

    def test_new_project_success_no_warnings(self):
        """Test `pyhatchery new project_name` succeeds with no warnings."""
        project_name = "my-new-project"
        normalized_name = project_name

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        self.assertIn(f"Creating new project: {normalized_name}\n", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}\n", stdout)

        self.assertIn("Derived PyPI slug: my-new-project", stderr)
        self.assertIn("Derived Python package slug: mocked_python_slug", stderr)
        self.assertNotIn("Warning:", stderr)

        self.assertEqual(exit_code, 0)
        self.mock_pep503_ok.assert_called_once_with(project_name)
        self.mock_normalize.assert_called_once_with(project_name)
        self.mock_derive_python_slug.assert_called_once_with(normalized_name)
        self.mock_check_pypi.assert_called_once_with(normalized_name)
        self.mock_is_valid_python_name.assert_called_once_with("mocked_python_slug")
        self.mock_collect_details.assert_called_once_with(normalized_name, [])

    def test_new_project_no_name_ac2(self):
        """Test `pyhatchery new` without project name displays error and help (AC2)."""
        stdout, stderr, exit_code, mock_exit = run_cli_capture_output(["new"])

        self.assertTrue(
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )
        self.assertIn(
            "error: the following arguments are required: project_name", stderr
        )
        self.assertEqual(stdout, "")
        self.assertEqual(exit_code, 2)
        mock_exit.assert_called_once_with(2)

    def test_new_project_empty_name_string_ac3(self):
        """Test `pyhatchery new ""` (empty project name) results in an error (AC3)."""
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", ""])

        self.assertIn("Error: Project name cannot be empty.", stderr)
        self.assertTrue(
            "usage: pyhatchery new [-h] project_name" in stderr
            or "usage: pyhatchery new project_name" in stderr
        )
        self.assertEqual(stdout, "")
        self.assertEqual(exit_code, 1)

    def test_new_project_initial_name_invalid_warning(self):
        """Test warning for initial project name format error."""
        self.mock_pep503_ok.return_value = (False, "Initial name format error.")
        self.mock_normalize.return_value = "pypi-slug"
        self.mock_derive_python_slug.return_value = "python_slug"

        invalid_name = "Invalid_Project_Name_Caps"
        normalized_name_mock = "pypi-slug"

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", invalid_name])

        expected_warning = (
            f"Warning: Project name '{invalid_name}': Initial name format error."
        )
        self.assertIn(f"Creating new project: {normalized_name_mock}", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}", stdout)
        self.assertIn(expected_warning, stderr)
        self.assertIn("Derived PyPI slug: pypi-slug", stderr)
        self.assertIn("Derived Python package slug: python_slug", stderr)
        self.assertEqual(exit_code, 0)

        self.mock_pep503_ok.assert_called_once_with(invalid_name)
        self.mock_collect_details.assert_called_once_with(normalized_name_mock, [])

    def test_new_project_pypi_name_taken_warning(self):
        """Test warning when derived PyPI name is likely taken."""
        self.mock_normalize.return_value = "taken-pypi-name"
        self.mock_derive_python_slug.return_value = "valid_python_slug"
        self.mock_check_pypi.return_value = (True, None)

        project_name = "someproject"
        normalized_name_mock = "taken-pypi-name"

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        warning_msg = (
            "Warning: The name 'taken-pypi-name' might already be taken on PyPI."
        )
        self.assertIn(f"Creating new project: {normalized_name_mock}", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}", stdout)
        self.assertIn(warning_msg, stderr)
        self.assertEqual(exit_code, 0)

        expected_warnings = [
            "The name 'taken-pypi-name' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        ]
        self.mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    def test_new_project_pypi_check_fails_warning(self):
        """Test warning when PyPI availability check fails."""
        self.mock_normalize.return_value = "pypi-name"
        self.mock_derive_python_slug.return_value = "valid_python_slug"
        self.mock_check_pypi.return_value = (None, "Network error during PyPI check")

        project_name = "someproject"
        normalized_name_mock = "pypi-name"

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        warning_msg = (
            "Warning: PyPI availability check for 'pypi-name' failed: "
            "Network error during PyPI check"
        )
        self.assertIn(f"Creating new project: {normalized_name_mock}", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}", stdout)
        self.assertIn(warning_msg, stderr)
        self.assertEqual(exit_code, 0)

        expected_warnings = [warning_msg.replace("Warning: ", "")]
        self.mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    def test_new_project_invalid_python_slug_warning(self):
        """Test warning when derived Python package slug is not PEP 8 compliant."""
        self.mock_normalize.return_value = "someprojectwithcaps"
        self.mock_derive_python_slug.return_value = "Invalid_Python_Slug"
        self.mock_is_valid_python_name.return_value = (False, "Not PEP 8 compliant.")

        project_name = "SomeProjectWithCaps"
        normalized_name_mock = "someprojectwithcaps"

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        warning_msg = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'someprojectwithcaps') is not PEP 8 compliant: "
            "Not PEP 8 compliant."
        )
        self.assertIn(f"Creating new project: {normalized_name_mock}", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}", stdout)
        self.assertIn(warning_msg, stderr)
        self.assertEqual(exit_code, 0)

        expected_warnings = [warning_msg.replace("Warning: ", "")]
        self.mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings
        )

    def test_new_project_all_warnings_and_proceeds(self):
        """Test CLI proceeds correctly when multiple warnings are present."""
        self.mock_pep503_ok.return_value = (False, "Initial name problem.")
        self.mock_normalize.return_value = "problematicname"
        self.mock_derive_python_slug.return_value = "Invalid_Python_Slug"
        self.mock_check_pypi.return_value = (True, None)
        self.mock_is_valid_python_name.return_value = (False, "Python slug invalid.")

        project_name = "ProblematicName"
        normalized_name_mock = "problematicname"

        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        self.assertIn(f"Creating new project: {normalized_name_mock}", stdout)
        self.assertIn("With details: {'author_name': 'Test Author'}", stdout)
        self.assertIn(
            f"Warning: Project name '{project_name}': Initial name problem.", stderr
        )
        self.assertIn(
            "Warning: The name 'problematicname' might already be taken on PyPI.",
            stderr,
        )
        warning_python_slug_msg = (
            "Warning: Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'problematicname') is not PEP 8 compliant: "
            "Python slug invalid."
        )
        self.assertIn(warning_python_slug_msg, stderr)
        self.assertIn("Derived PyPI slug: problematicname", stderr)
        self.assertIn("Derived Python package slug: Invalid_Python_Slug", stderr)
        self.assertEqual(exit_code, 0)

        expected_warnings_list = [
            "The name 'problematicname' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly.",
            "Derived Python package name 'Invalid_Python_Slug' "
            "(from input 'problematicname') is not PEP 8 compliant: "
            "Python slug invalid.",
        ]
        self.mock_collect_details.assert_called_once_with(
            normalized_name_mock, expected_warnings_list
        )

    def test_no_command_provided(self):
        """Test `pyhatchery` without a command shows help and exits."""
        stdout, stderr, exit_code, _ = run_cli_capture_output([])

        self.assertIn("PyHatchery: A Python project scaffolding tool.", stderr)
        self.assertIn("Commands:", stderr)
        self.assertIn("new", stderr)
        self.assertEqual(stdout, "")
        self.assertEqual(exit_code, 1)
