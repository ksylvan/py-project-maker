"""
Unit tests for the config_loader component.
"""

import subprocess
from pathlib import Path
from typing import Callable  # Ensure Callable is imported
from unittest.mock import MagicMock, patch

import pytest

from pyhatchery.components.config_loader import get_git_config_value, load_from_env

# Test data for .env file
ENV_CONTENT_VALID = """
AUTHOR_NAME="Test Env Author"
AUTHOR_EMAIL="env@example.com"
# This is a comment
INVALID_LINE
PROJECT_DESCRIPTION = "A project from .env"
"""

ENV_CONTENT_EMPTY = ""


@pytest.fixture
def temp_env_file(tmp_path: Path) -> Callable[..., Path]:  # Added return type hint
    """Fixture to create a temporary .env file."""

    def _create_env_file(
        content: str, filename: str = ".env"
    ) -> Path:  # Added return type hint
        env_file = tmp_path / filename
        env_file.write_text(content)
        return env_file

    return _create_env_file


class TestGetGitConfigValue:
    """Tests for the get_git_config_value function."""

    @patch("subprocess.run")
    def test_get_git_config_value_success(self, mock_subprocess_run: MagicMock):
        """Test successfully retrieving a git config value."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "Test User\n"
        mock_subprocess_run.return_value = mock_process

        result = get_git_config_value("user.name")
        assert result == "Test User"
        mock_subprocess_run.assert_called_once_with(
            ["git", "config", "--get", "user.name"],
            capture_output=True,
            text=True,
            check=False,
        )

    @patch("subprocess.run")
    def test_get_git_config_value_not_set(self, mock_subprocess_run: MagicMock):
        """Test when the git config value is not set (git command returns non-zero)."""
        mock_process = MagicMock()
        mock_process.returncode = 1  # Value not set
        mock_process.stdout = ""
        mock_subprocess_run.return_value = mock_process

        result = get_git_config_value("user.nonexistent")
        assert result is None

    @patch("subprocess.run")
    def test_get_git_config_value_git_not_found(self, mock_subprocess_run: MagicMock):
        """Test when the git command is not found."""
        mock_subprocess_run.side_effect = FileNotFoundError
        result = get_git_config_value("user.name")
        assert result is None

    @patch("subprocess.run")
    def test_get_git_config_value_other_subprocess_error(
        self, mock_subprocess_run: MagicMock
    ):
        """Test handling of other unexpected subprocess errors."""
        mock_subprocess_run.side_effect = subprocess.SubprocessError("Some error")
        result = get_git_config_value("user.name")
        assert result is None


class TestLoadFromEnv:
    """Tests for the load_from_env function."""

    @patch("dotenv.dotenv_values")  # Corrected patch target
    def test_load_from_env_success(
        self,
        mock_dotenv_values: MagicMock,
        temp_env_file: Callable[..., Path],  # pylint: disable=redefined-outer-name
    ):
        """Test successfully loading variables from an .env file."""
        env_file_path = temp_env_file(ENV_CONTENT_VALID)
        expected_dict = {
            "AUTHOR_NAME": "Test Env Author",
            "AUTHOR_EMAIL": "env@example.com",
            "PROJECT_DESCRIPTION": "A project from .env",
        }
        # Note: python-dotenv's dotenv_values handles comments and invalid lines.
        # We mock its return value based on expected behavior.
        mock_dotenv_values.return_value = expected_dict

        result = load_from_env(str(env_file_path))
        assert result == expected_dict
        mock_dotenv_values.assert_called_once_with(dotenv_path=env_file_path)

    @patch("dotenv.dotenv_values")  # Corrected patch target
    def test_load_from_env_file_not_found(
        self, mock_dotenv_values: MagicMock, tmp_path: Path
    ):
        """Test when the .env file does not exist."""
        # This test relies on the internal check `env_path.is_file()` failing first.
        # So, mock_dotenv_values should not be called.
        non_existent_env_file = tmp_path / "non_existent.env"
        result = load_from_env(str(non_existent_env_file))
        assert result == {}
        mock_dotenv_values.assert_not_called()

    @patch("dotenv.dotenv_values")  # Corrected patch target
    def test_load_from_env_empty_file(
        self,
        mock_dotenv_values: MagicMock,
        temp_env_file: Callable[..., Path],  # pylint: disable=redefined-outer-name
    ):
        """Test loading from an empty .env file."""
        env_file_path = temp_env_file(ENV_CONTENT_EMPTY)
        mock_dotenv_values.return_value = {}  # dotenv_values returns {} for empty file

        result = load_from_env(str(env_file_path))
        assert result == {}
        mock_dotenv_values.assert_called_once_with(dotenv_path=env_file_path)

    @patch("pyhatchery.components.config_loader.Path.is_file")
    @patch("dotenv.dotenv_values")  # Corrected patch target
    def test_load_from_env_default_path_exists(
        self, mock_dotenv_values: MagicMock, mock_is_file: MagicMock
    ):
        """Test loading from default '.env' when it exists."""
        mock_is_file.return_value = True  # Simulate .env exists
        expected_dict = {"DEFAULT_KEY": "DefaultValue"}
        mock_dotenv_values.return_value = expected_dict

        result = load_from_env()  # Call with default path
        assert result == expected_dict
        mock_dotenv_values.assert_called_once()
        # Check kwargs as dotenv_path is passed as a keyword argument
        assert mock_dotenv_values.call_args.kwargs.get("dotenv_path") == Path(".env")

    @patch("pyhatchery.components.config_loader.Path.is_file")
    @patch("dotenv.dotenv_values")  # Corrected patch target
    def test_load_from_env_default_path_not_exists(
        self, mock_dotenv_values: MagicMock, mock_is_file: MagicMock
    ):
        """Test loading from default '.env' when it does not exist."""
        mock_is_file.return_value = False  # Simulate .env does not exist
        result = load_from_env()  # Call with default path
        assert result == {}
        mock_dotenv_values.assert_not_called()
