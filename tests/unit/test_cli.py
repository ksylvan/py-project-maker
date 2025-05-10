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

    def test_new_project_success_ac1_ac4(self):
        """AC1: Running `pyhatchery new my_new_project` executes successfully.
        AC4: The provided `project_name` is correctly captured."""
        project_name = "my_new_project"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", project_name])

        assert f"Creating new project: {project_name}" in stdout
        assert stderr == ""
        assert exit_code == 0

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

    def test_new_project_invalid_chars_ac3(self):
        """AC3: Invalid project names (invalid characters) result in an error."""
        invalid_name = "invalid!name"
        stdout, stderr, exit_code, _ = run_cli_capture_output(["new", invalid_name])

        assert (
            f"Error: Project name '{invalid_name}' violates PEP 503 conventions."
            in stderr
        )
        assert stdout == ""
        assert exit_code == 1
        # mock_exit is not called here because main() returns directly

    def test_no_command_provided(self):
        """Test that running `pyhatchery` without a command shows help."""
        stdout, stderr, exit_code, _ = run_cli_capture_output([])

        assert (
            "usage: pyhatchery [-h] {new} ..." in stderr
        )  # Basic check for help output
        assert "PyHatchery: A Python project scaffolding tool." in stderr  # Description
        assert "Commands:" in stderr
        assert "new" in stderr  # 'new' command should be listed
        assert stdout == ""
        assert exit_code == 1  # Our cli.py returns 1 if command is None
        # mock_exit is not called here because main() returns directly
