"""Unit tests for the PyHatchery CLI non-interactive mode."""

import io
import os
from unittest.mock import MagicMock, patch

# We access a private function for testing purposes
from pyhatchery.cli import (
    internal_get_project_details_non_interactive_for_testing,
    main,
)
from pyhatchery.components.interactive_wizard import (
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
)


class TestNonInteractiveMode:
    """Tests for the non-interactive mode functionality."""

    mock_load_env: MagicMock
    mock_pep503_ok: MagicMock
    mock_normalize: MagicMock
    mock_derive_slug: MagicMock
    mock_check_pypi: MagicMock
    mock_is_valid: MagicMock

    def setup_method(self):
        """Set up common test mocks and environment."""
        self.mock_load_env = patch("pyhatchery.cli.load_from_env").start()
        self.mock_pep503_ok = patch("pyhatchery.cli.pep503_name_ok").start()
        self.mock_normalize = patch("pyhatchery.cli.pep503_normalize").start()
        self.mock_derive_slug = patch(
            "pyhatchery.cli.derive_python_package_slug"
        ).start()
        self.mock_check_pypi = patch("pyhatchery.cli.check_pypi_availability").start()
        self.mock_is_valid = patch(
            "pyhatchery.cli.is_valid_python_package_name"
        ).start()

        self.mock_pep503_ok.return_value = (True, None)
        self.mock_normalize.return_value = "test-project"
        self.mock_derive_slug.return_value = "test_project"
        self.mock_check_pypi.return_value = (False, None)
        self.mock_is_valid.return_value = (True, None)
        self.mock_load_env.return_value = {}

    def teardown_method(self):
        """Clean up patches and environment after tests."""
        patch.stopall()
        if "PYHATCHERY_DEBUG" in os.environ:
            os.environ.pop("PYHATCHERY_DEBUG")

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    @patch("pyhatchery.cli.str_to_bool", return_value=True)  # Force debug mode
    def test_cli_non_interactive_mode_with_cli_args(
        self,
        _mock_str_to_bool: MagicMock,
        mock_exit: MagicMock,
        _mock_stderr: MagicMock,
        mock_stdout: MagicMock,
    ):
        """Test non-interactive mode with arguments provided via CLI."""
        # Set debug flag through environment
        os.environ["PYHATCHERY_DEBUG"] = "1"

        argv = [
            "new",
            "test-project",
            "--no-interactive",
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
            "--github-username",
            "testuser",
            "--description",
            "A test project",
            "--license",
            "MIT",
            "--python-version",
            "3.11",
        ]

        main(argv)

        output = mock_stdout.getvalue()
        assert "Creating new project: test-project" in output
        assert "With details:" in output
        assert "Test Author" in output

        # Ensure we didn't call sys.exit with an error code
        if mock_exit.called:
            args, _ = mock_exit.call_args
            assert args[0] == 0

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    @patch("pyhatchery.cli.str_to_bool", return_value=True)  # Force debug mode
    def test_cli_non_interactive_mode_with_env_values(
        self,
        _mock_str_to_bool: MagicMock,
        mock_exit: MagicMock,
        _mock_stderr: MagicMock,
        mock_stdout: MagicMock,
    ):
        """Test non-interactive mode with values from .env file."""
        self.mock_load_env.return_value = {
            "AUTHOR_NAME": "Env Author",
            "AUTHOR_EMAIL": "env@example.com",
            "GITHUB_USERNAME": "envuser",
            "PROJECT_DESCRIPTION": "A project from env",
            "LICENSE": "Apache-2.0",
            "PYTHON_VERSION": "3.12",
        }

        # Enable debug mode
        os.environ["PYHATCHERY_DEBUG"] = "1"

        argv = ["new", "test-project", "--no-interactive"]
        main(argv)

        output = mock_stdout.getvalue()
        assert "Creating new project: test-project" in output
        assert "With details:" in output
        assert "Env Author" in output

        # Ensure we didn't call sys.exit with an error code
        if mock_exit.called:
            args, _ = mock_exit.call_args
            assert args[0] == 0

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    def test_cli_non_interactive_mode_with_missing_required_fields(
        self, _mock_exit: MagicMock, mock_stderr: MagicMock, _mock_stdout: MagicMock
    ):
        """Test non-interactive mode fails when required fields are missing."""
        # Reset all previous mock return values
        self.mock_load_env.return_value = {}

        # Call main with non-interactive mode but without required fields
        argv = ["new", "test-project", "--no-interactive"]

        result = main(argv)

        # Verify that main returns exit code 1
        assert result == 1

        # Check that error message was printed
        error_output = mock_stderr.getvalue()
        assert "Error: The following required fields are missing" in error_output
        assert "author_name" in error_output
        assert "author_email" in error_output

    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("sys.exit")
    @patch("pyhatchery.cli.str_to_bool", return_value=True)  # Force debug mode
    def test_cli_non_interactive_mode_precedence(
        self,
        _mock_str_to_bool: MagicMock,
        _mock_exit: MagicMock,
        _mock_stderr: MagicMock,
        mock_stdout: MagicMock,
    ):
        """Test that CLI args take precedence over .env values."""
        # Set up .env values
        self.mock_load_env.return_value = {
            "AUTHOR_NAME": "Env Author",
            "AUTHOR_EMAIL": "env@example.com",
            "GITHUB_USERNAME": "envuser",
            "PROJECT_DESCRIPTION": "A project from env",
            "LICENSE": "GPL-3.0",
            "PYTHON_VERSION": "3.10",
        }

        # Enable debug mode
        os.environ["PYHATCHERY_DEBUG"] = "1"

        # CLI args should override .env values
        argv = [
            "new",
            "test-project",
            "--no-interactive",
            "--author",
            "CLI Author",  # Override env
            "--license",
            "MIT",  # Override env
        ]

        main(argv)

        output = mock_stdout.getvalue()
        assert "Creating new project: test-project" in output
        assert "CLI Author" in output  # CLI value

        # Check debug output for details
        os.environ["PYHATCHERY_DEBUG"] = "1"
        argv.append("--debug")
        mock_stdout.truncate(0)
        mock_stdout.seek(0)

        main(argv)
        debug_output = mock_stdout.getvalue()

        # CLI args should take precedence
        assert "CLI Author" in debug_output
        assert "env@example.com" in debug_output  # Env value not overridden
        assert "MIT" in debug_output  # CLI value

        os.environ.pop("PYHATCHERY_DEBUG", None)

    def test_get_project_details_non_interactive_warnings(self):
        """Test warnings are displayed in non-interactive mode."""
        args_mock = MagicMock()
        args_mock.author = "Test Author"
        args_mock.email = "test@example.com"
        args_mock.github_username = None
        args_mock.description = None
        args_mock.license = None
        args_mock.python_version = None

        name_warnings = ["Warning 1", "Warning 2"]

        with patch("pyhatchery.cli.click.secho") as mock_secho:
            result = internal_get_project_details_non_interactive_for_testing(
                args_mock, name_warnings, "test-project"
            )

            # Check that warnings are displayed
            assert mock_secho.call_count >= 3
            # First call should be the warning header
            args, _ = mock_secho.call_args_list[0]
            assert "warnings" in args[0].lower()

        assert result is not None
        assert result["author_name"] == "Test Author"
        assert result["author_email"] == "test@example.com"
        assert result["license"] == DEFAULT_LICENSE  # Default used

    def test_get_project_details_merges_sources_correctly(self):
        """Test that _get_project_details_non_interactive correctly merges sources."""
        args_mock = MagicMock()
        args_mock.author = "CLI Author"  # CLI provided
        args_mock.email = None  # Not provided via CLI
        args_mock.github_username = None
        args_mock.description = None
        args_mock.license = None
        args_mock.python_version = None

        # Set up env values
        self.mock_load_env.return_value = {
            "AUTHOR_EMAIL": "env@example.com",  # Env provided
            "PROJECT_DESCRIPTION": "Description from env",
        }

        result = internal_get_project_details_non_interactive_for_testing(
            args_mock, [], "test-project"
        )

        assert result is not None
        assert result["author_name"] == "CLI Author"  # From CLI
        assert result["author_email"] == "env@example.com"  # From .env
        assert result["project_description"] == "Description from env"  # From .env
        assert result["license"] == DEFAULT_LICENSE  # Default
        assert result["python_version_preference"] == DEFAULT_PYTHON_VERSION  # Default
