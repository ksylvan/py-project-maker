"""
Unit tests for the interactive_wizard component.
"""

import unittest
from unittest.mock import MagicMock, call, patch

from pyhatchery.components.interactive_wizard import (
    COMMON_LICENSES,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    PYTHON_VERSIONS,
    collect_project_details,
    prompt_for_choice,
    prompt_for_value,
)

MODULE_PATH = "pyhatchery.components.interactive_wizard"


class TestPromptForValue(unittest.TestCase):
    """Tests for the _prompt_for_value helper function."""

    @patch(f"{MODULE_PATH}.input")
    def test_prompt_with_default_user_provides_value(self, mock_input: MagicMock):
        """Test when a default is provided and user enters a value."""
        mock_input.return_value = "User Value"
        result = prompt_for_value("Enter something", "Default Value")
        assert result == "User Value"
        mock_input.assert_called_once_with("Enter something (default: Default Value): ")

    @patch(f"{MODULE_PATH}.input")
    def test_prompt_with_default_user_accepts_default(self, mock_input: MagicMock):
        """Test when a default is provided and user presses Enter (empty input)."""
        mock_input.return_value = ""
        result = prompt_for_value("Enter something", "Default Value")
        assert result == "Default Value"

    @patch(f"{MODULE_PATH}.input")
    def test_prompt_no_default_user_provides_value(self, mock_input: MagicMock):
        """Test when no default is provided and user enters a value."""
        mock_input.return_value = "User Value"
        result = prompt_for_value("Enter something")
        assert result == "User Value"
        mock_input.assert_called_once_with("Enter something: ")

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")
    def test_prompt_no_default_user_enters_empty_then_value(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test no default, user enters empty string then a valid value."""
        mock_input.side_effect = ["", "User Value"]
        result = prompt_for_value("Enter something")
        assert result == "User Value"
        assert mock_input.call_count == 2
        mock_click.secho.assert_called_once_with(
            "This field cannot be empty.", fg="red"
        )


class TestPromptForChoice:
    """Tests for the _prompt_for_choice helper function."""

    choices = ["Alpha", "Beta", "Gamma"]
    default = "Beta"

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")
    def test_selects_valid_choice_by_number(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test selecting a valid choice by its number."""
        mock_input.return_value = "1"
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Alpha"
        expected_calls = [
            call.secho("Choose:", fg="cyan"),
            call.secho("  1. Alpha"),
            call.secho("  2. Beta", fg="green", bold=True, nl=False),
            call.secho(" (default)", fg="green"),
            call.secho("  3. Gamma"),
        ]
        mock_click.assert_has_calls(expected_calls, any_order=True)

    @patch(f"{MODULE_PATH}.input")
    def test_accepts_default_choice_on_enter(self, mock_input: MagicMock):
        """Test accepting the default choice by pressing Enter."""
        mock_input.return_value = ""
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == self.default

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")
    def test_handles_invalid_numeric_choice_then_valid(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test handling invalid numeric choices before a valid one."""
        mock_input.side_effect = ["0", "4", "2"]
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Beta"
        assert mock_input.call_count == 3
        error_message = f"Invalid choice. Enter a number from 1 to {len(self.choices)}."
        initial_secho_calls = 1 + len(self.choices) + 1
        calls_to_check = mock_click.method_calls[initial_secho_calls:]
        assert all(
            call.secho(error_message, fg="red") in calls_to_check
            for _ in range(mock_input.call_count - 1)
        )

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")
    def test_handles_non_numeric_choice_then_valid(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test handling of non-numeric input before a valid numeric choice."""
        mock_input.side_effect = ["abc", "3"]
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Gamma"
        assert mock_input.call_count == 2
        assert (
            call.secho("Invalid input. Please enter a number.", fg="red")
            in mock_click.method_calls
        )


class TestCollectProjectDetails:
    """Tests for the main collect_project_details function."""

    PROJECT_NAME = "Test Project"

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.prompt_for_value")
    @patch(f"{MODULE_PATH}.prompt_for_choice")
    @patch(f"{MODULE_PATH}.input")
    def test_collects_all_details_no_warnings(
        self,
        mock_proceed_input: MagicMock,
        mock_prompt_choice: MagicMock,
        mock_prompt_value: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting all details when there are no name warnings."""
        mock_get_git_config.side_effect = ["Git User", "git@example.com"]
        mock_prompt_value.side_effect = [
            "Test Author",
            "test@example.com",
            "testuser",
            "A test project",
        ]
        mock_prompt_choice.side_effect = ["MIT", "3.11"]
        mock_proceed_input.return_value = "yes"

        result = collect_project_details(self.PROJECT_NAME, name_warnings=None)

        assert result is not None
        assert result["author_name"] == "Test Author"
        assert result["author_email"] == "test@example.com"
        assert result["github_username"] == "testuser"
        assert result["project_description"] == "A test project"
        assert result["license"] == "MIT"
        assert result["python_version_preference"] == "3.11"

        mock_get_git_config.assert_has_calls([call("user.name"), call("user.email")])
        assert mock_prompt_value.call_count == 4
        assert mock_prompt_choice.call_count == 2
        mock_proceed_input.assert_not_called()

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.prompt_for_value")
    @patch(f"{MODULE_PATH}.prompt_for_choice")
    @patch(f"{MODULE_PATH}.input")
    def test_collects_details_with_warnings_user_proceeds(
        self,
        mock_proceed_input: MagicMock,
        mock_prompt_choice: MagicMock,
        mock_prompt_value: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting details when warnings exist and user proceeds."""
        warnings = ["Name too short", "Name invalid"]
        mock_proceed_input.return_value = "yes"

        mock_get_git_config.side_effect = [None, None]
        mock_prompt_value.side_effect = [
            "Author From Prompt",
            "email@prompt.com",
            "gh_user_prompt",
            "Desc Prompt",
        ]
        mock_prompt_choice.side_effect = [DEFAULT_LICENSE, DEFAULT_PYTHON_VERSION]

        result = collect_project_details(self.PROJECT_NAME, name_warnings=warnings)

        assert result is not None
        assert result["author_name"] == "Author From Prompt"
        assert result["author_email"] == "email@prompt.com"
        assert result["github_username"] == "gh_user_prompt"
        mock_proceed_input.assert_called_once_with(
            "Ignore warnings and proceed with this name? (yes/no, default: yes): "
        )

    @patch(f"{MODULE_PATH}.input")
    def test_exits_if_user_does_not_proceed_after_warnings(
        self, mock_proceed_input: MagicMock
    ):
        """Test that function returns None if user chooses not to proceed."""
        warnings = ["Name conflict"]
        mock_proceed_input.return_value = "no"

        result = collect_project_details(self.PROJECT_NAME, name_warnings=warnings)
        assert result is None
        mock_proceed_input.assert_called_once()

    @patch(f"{MODULE_PATH}.get_git_config_value", side_effect=[None, None])
    @patch(f"{MODULE_PATH}.prompt_for_value")
    @patch(f"{MODULE_PATH}.prompt_for_choice")
    def test_uses_defaults_when_git_config_missing_and_prompts_return_defaults(
        self,
        mock_prompt_choice: MagicMock,
        mock_prompt_value: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test defaults used if git config missing & prompts accept defaults."""
        mock_prompt_value.side_effect = [
            "Default Author",
            "default@example.com",
            "default_gh",
            "Default Description",
        ]
        mock_prompt_choice.side_effect = [DEFAULT_LICENSE, DEFAULT_PYTHON_VERSION]

        result = collect_project_details(self.PROJECT_NAME, name_warnings=None)

        assert result is not None
        assert result["author_name"] == "Default Author"
        assert result["author_email"] == "default@example.com"
        assert result["github_username"] == "default_gh"
        assert result["project_description"] == "Default Description"
        assert result["license"] == DEFAULT_LICENSE
        assert result["python_version_preference"] == DEFAULT_PYTHON_VERSION

        mock_get_git_config.assert_has_calls([call("user.name"), call("user.email")])

        expected_prompt_value_calls = [
            call("Author Name", None),
            call("Author Email", None),
            call("GitHub Username"),
            call("Project Description"),
        ]
        mock_prompt_value.assert_has_calls(expected_prompt_value_calls)

        expected_prompt_choice_calls = [
            call("Select License:", COMMON_LICENSES, DEFAULT_LICENSE),
            call("Select Python Version:", PYTHON_VERSIONS, DEFAULT_PYTHON_VERSION),
        ]
        mock_prompt_choice.assert_has_calls(expected_prompt_choice_calls)
