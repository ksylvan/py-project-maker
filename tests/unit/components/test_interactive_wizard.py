"""
Unit tests for the interactive_wizard component.
"""

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


class TestPromptForValue:
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
        mock_input.return_value = ""  # User presses Enter
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
    @patch(f"{MODULE_PATH}.click")  # To capture click calls for "cannot be empty"
    def test_prompt_no_default_user_enters_empty_then_value(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test no default, user enters empty string then a valid value."""
        mock_input.side_effect = ["", "User Value"]  # First empty, then value
        result = prompt_for_value("Enter something")
        assert result == "User Value"
        assert mock_input.call_count == 2
        # Updated assertion to check for click.secho with fg='red'
        mock_click.secho.assert_called_once_with(
            "This field cannot be empty.", fg="red"
        )


class TestPromptForChoice:
    """Tests for the _prompt_for_choice helper function."""

    choices = ["Alpha", "Beta", "Gamma"]
    default = "Beta"

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")  # To check prompts
    def test_selects_valid_choice_by_number(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test selecting a valid choice by its number."""
        mock_input.return_value = "1"  # Selects "Alpha"
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Alpha"
        # Check that choices were printed correctly
        expected_calls = [
            call.secho("Choose:", fg="cyan"),
            call.secho("  1. Alpha"),
            call.secho("  2. Beta", fg="green", bold=True, nl=False),
            call.secho(" (default)", fg="green"),
            call.secho("  3. Gamma"),
        ]
        mock_click.assert_has_calls(expected_calls, any_order=True)
        # Updated to check mock_click.method_calls directly

    @patch(f"{MODULE_PATH}.input")
    def test_accepts_default_choice_on_enter(self, mock_input: MagicMock):
        """Test accepting the default choice by pressing Enter."""
        mock_input.return_value = ""  # User presses Enter
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == self.default

    @patch(f"{MODULE_PATH}.input")
    @patch(f"{MODULE_PATH}.click")
    def test_handles_invalid_numeric_choice_then_valid(
        self, mock_click: MagicMock, mock_input: MagicMock
    ):
        """Test handling invalid numeric choices before a valid one."""
        mock_input.side_effect = ["0", "4", "2"]  # Invalid, Invalid, Valid ("Beta")
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Beta"
        assert mock_input.call_count == 3
        # Check that error messages were printed
        error_message = f"Invalid choice. Enter a number from 1 to {len(self.choices)}."
        # Check error messages were printed for each invalid input.
        # Skips initial prompt and choice listing.
        # The number of initial secho calls for prompt and choices:
        # 1 for prompt_message
        # 1 for each choice (self.choices)
        # 1 extra for the default choice's "(default)" part
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
        mock_input.side_effect = ["abc", "3"]  # Invalid, Valid ("Gamma")
        result = prompt_for_choice("Choose:", self.choices, self.default)
        assert result == "Gamma"
        assert mock_input.call_count == 2
        # Updated assertion to check for click.secho with fg='red'
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
    @patch(f"{MODULE_PATH}.input")  # For the "proceed?" prompt
    def test_collects_all_details_no_warnings(
        self,
        mock_proceed_input: MagicMock,
        mock_prompt_choice: MagicMock,
        mock_prompt_value: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting all details when there are no name warnings."""
        mock_get_git_config.side_effect = ["Git User", "git@example.com"]  # name, email
        mock_prompt_value.side_effect = [
            "Test Author",  # Author Name (overrides git)
            "test@example.com",  # Author Email (overrides git)
            "testuser",  # GitHub Username
            "A test project",  # Project Description
        ]
        mock_prompt_choice.side_effect = ["MIT", "3.11"]  # License, Python Version
        mock_proceed_input.return_value = "yes"  # Should not be called if no warnings

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
        mock_proceed_input.assert_not_called()  # No warnings, so no proceed prompt

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.prompt_for_value")
    @patch(f"{MODULE_PATH}.prompt_for_choice")
    @patch(f"{MODULE_PATH}.input")  # For the "proceed?" prompt
    def test_collects_details_with_warnings_user_proceeds(
        self,
        mock_proceed_input: MagicMock,
        mock_prompt_choice: MagicMock,
        mock_prompt_value: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting details when warnings exist and user proceeds."""
        warnings = ["Name too short", "Name invalid"]
        mock_proceed_input.return_value = "yes"  # User proceeds

        mock_get_git_config.side_effect = [None, None]  # No git defaults
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

    @patch(f"{MODULE_PATH}.input")  # For the "proceed?" prompt
    def test_exits_if_user_does_not_proceed_after_warnings(
        self, mock_proceed_input: MagicMock
    ):
        """Test that function returns None if user chooses not to proceed."""
        warnings = ["Name conflict"]
        mock_proceed_input.return_value = "no"  # User does not proceed

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
        # _prompt_for_value will return its default if input is empty
        # _prompt_for_choice will return its default if input is empty
        # Simulate this by having them return expected default values
        mock_prompt_value.side_effect = [
            "Default Author",  # Assumes _prompt_for_value returns this
            "default@example.com",
            "default_gh",
            "Default Description",
        ]
        mock_prompt_choice.side_effect = [DEFAULT_LICENSE, DEFAULT_PYTHON_VERSION]

        result = collect_project_details(self.PROJECT_NAME, name_warnings=None)

        assert result is not None
        # The actual default for author/email if git is None and input is empty
        # depends on how _prompt_for_value handles a None default.
        # The current _prompt_for_value requires input if default is None.
        # So, this test setup implies the user *typed* these "Default Author" values.
        assert result["author_name"] == "Default Author"
        assert result["author_email"] == "default@example.com"
        assert result["github_username"] == "default_gh"
        assert result["project_description"] == "Default Description"
        assert result["license"] == DEFAULT_LICENSE
        assert result["python_version_preference"] == DEFAULT_PYTHON_VERSION

        # Check that get_git_config_value was called
        mock_get_git_config.assert_has_calls([call("user.name"), call("user.email")])

        # Check that _prompt_for_value was called for each field
        # Defaults for author name/email passed to _prompt_for_value would be None.
        expected_prompt_value_calls = [
            call("Author Name", None),
            call("Author Email", None),
            call("GitHub Username"),  # No default passed
            call("Project Description"),  # No default passed
        ]
        mock_prompt_value.assert_has_calls(expected_prompt_value_calls)

        # Check that _prompt_for_choice was called for license and python version
        expected_prompt_choice_calls = [
            call("Select License:", COMMON_LICENSES, DEFAULT_LICENSE),
            call("Select Python Version:", PYTHON_VERSIONS, DEFAULT_PYTHON_VERSION),
        ]
        mock_prompt_choice.assert_has_calls(expected_prompt_choice_calls)
