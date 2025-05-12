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


@pytest.fixture(name="temp_env_file")
def temp_env_file_fixture(
    tmp_path: Path,
) -> Callable[..., Path]:  # Added return type hint
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

    @patch("pyhatchery.components.config_loader.Path")  # Outer patch
    @patch("pyhatchery.components.config_loader.dotenv_values")  # Inner patch
    def test_load_from_env_success(
        self,
        mock_dotenv_values_in_cl: MagicMock,  # Inner patch arg
        mock_path_in_cl: MagicMock,  # Outer patch arg
        temp_env_file: Callable[..., Path],  # Using the correct fixture name
    ):
        """Test successfully loading variables from an .env file."""
        real_env_file_path_obj = temp_env_file(ENV_CONTENT_VALID)
        real_env_file_path_str = str(real_env_file_path_obj)

        # Configure the mock for Path class instantiation within config_loader
        # This mock_path_instance will be returned when Path(...) is called
        mock_path_instance = MagicMock(spec=Path)
        # Crucially, mock the is_file method on this instance
        mock_path_instance.is_file = MagicMock(return_value=True)
        mock_path_in_cl.return_value = mock_path_instance

        expected_loaded_vars = {
            "AUTHOR_NAME": "Test Env Author",
            "AUTHOR_EMAIL": "env@example.com",
            "PROJECT_DESCRIPTION": "A project from .env",
        }
        mock_dotenv_values_in_cl.return_value = expected_loaded_vars

        result = load_from_env(real_env_file_path_str)

        mock_path_in_cl.assert_called_once_with(real_env_file_path_str)
        mock_path_instance.is_file.assert_called_once()
        # dotenv_values should be called with the Path obj created in load_from_env
        mock_dotenv_values_in_cl.assert_called_once_with(dotenv_path=mock_path_instance)
        assert result == expected_loaded_vars

    @patch("pyhatchery.components.config_loader.Path")  # Outer
    @patch("pyhatchery.components.config_loader.dotenv_values")  # Inner
    def test_load_from_env_file_not_found(
        self,
        mock_dotenv_values_in_cl: MagicMock,  # Inner
        mock_path_in_cl: MagicMock,  # Outer
        tmp_path: Path,
    ):
        """Test when the .env file does not exist."""
        non_existent_env_file_str = str(tmp_path / "non_existent.env")

        mock_path_instance = MagicMock(spec=Path)
        mock_path_instance.is_file = MagicMock(return_value=False)  # Key for this test
        mock_path_in_cl.return_value = mock_path_instance

        result = load_from_env(non_existent_env_file_str)

        mock_path_in_cl.assert_called_once_with(non_existent_env_file_str)
        mock_path_instance.is_file.assert_called_once()
        mock_dotenv_values_in_cl.assert_not_called()
        assert result == {}

    @patch("pyhatchery.components.config_loader.Path")  # Outer
    @patch("pyhatchery.components.config_loader.dotenv_values")  # Inner
    def test_load_from_env_empty_file(
        self,
        mock_dotenv_values_in_cl: MagicMock,  # Inner
        mock_path_in_cl: MagicMock,  # Outer
        temp_env_file: Callable[..., Path],  # Using the correct fixture name
    ):
        """Test loading from an empty .env file."""
        real_env_file_path_obj = temp_env_file(ENV_CONTENT_EMPTY)
        real_env_file_path_str = str(real_env_file_path_obj)

        mock_path_instance = MagicMock(spec=Path)
        mock_path_instance.is_file = MagicMock(return_value=True)
        mock_path_in_cl.return_value = mock_path_instance

        mock_dotenv_values_in_cl.return_value = {}

        result = load_from_env(real_env_file_path_str)

        mock_path_in_cl.assert_called_once_with(real_env_file_path_str)
        mock_path_instance.is_file.assert_called_once()
        mock_dotenv_values_in_cl.assert_called_once_with(dotenv_path=mock_path_instance)
        assert result == {}

    @patch("pyhatchery.components.config_loader.Path")  # Outer
    @patch("pyhatchery.components.config_loader.dotenv_values")  # Inner
    def test_load_from_env_default_path_exists(
        self,
        mock_dotenv_values_in_cl: MagicMock,  # Inner
        mock_path_in_cl: MagicMock,  # Outer
    ):
        """Test loading from default '.env' when it exists."""
        mock_path_instance = MagicMock(spec=Path)
        mock_path_instance.is_file = MagicMock(return_value=True)
        mock_path_in_cl.return_value = mock_path_instance

        expected_vars_from_dotenv = {"DEFAULT_KEY": "DefaultValue"}
        mock_dotenv_values_in_cl.return_value = expected_vars_from_dotenv

        result = load_from_env()  # Call with default path ".env"

        mock_path_in_cl.assert_called_once_with(".env")
        mock_path_instance.is_file.assert_called_once()
        mock_dotenv_values_in_cl.assert_called_once_with(dotenv_path=mock_path_instance)
        assert result == expected_vars_from_dotenv

    @patch("pyhatchery.components.config_loader.Path")  # Outer
    @patch("pyhatchery.components.config_loader.dotenv_values")  # Inner
    def test_load_from_env_default_path_not_exists(
        self,
        mock_dotenv_values_in_cl: MagicMock,  # Inner
        mock_path_in_cl: MagicMock,  # Outer
    ):
        """Test loading from default '.env' when it does not exist."""
        mock_path_instance = MagicMock(spec=Path)
        mock_path_instance.is_file = MagicMock(return_value=False)
        mock_path_in_cl.return_value = mock_path_instance

        result = load_from_env()  # Call with default path

        mock_path_in_cl.assert_called_once_with(".env")
        mock_path_instance.is_file.assert_called_once()
        mock_dotenv_values_in_cl.assert_not_called()
        assert result == {}
