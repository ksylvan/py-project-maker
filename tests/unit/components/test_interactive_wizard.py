"""
Unit tests for the interactive_wizard component.
"""

from unittest.mock import MagicMock, call, patch

import click
from pytest import raises as expect_raise

from pyhatchery.components.interactive_wizard import (
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    collect_project_details,
)

MODULE_PATH = "pyhatchery.components.interactive_wizard"


# [Keep existing TestPromptForValue and TestPromptForChoice classes]


class TestCollectProjectDetails:
    """Tests for the main collect_project_details function."""

    PROJECT_NAME = "Test Project"

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.click.prompt")
    @patch(f"{MODULE_PATH}.click.confirm")
    def test_collects_all_details_no_warnings(
        self,
        mock_confirm: MagicMock,
        mock_prompt: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting all details when there are no name warnings."""
        mock_get_git_config.side_effect = ["Git User", "git@example.com", None]
        mock_prompt.side_effect = [
            "Test Author",  # author_name
            "test@example.com",  # author_email
            "testuser",  # github_username
            "A test project",  # project_description
            "MIT",  # license
            "3.11",  # python_version
        ]

        result = collect_project_details(
            self.PROJECT_NAME, name_warnings=[], cli_defaults={}
        )

        assert result is not None
        assert result["author_name"] == "Test Author"
        assert result["author_email"] == "test@example.com"
        assert result["github_username"] == "testuser"
        assert result["project_description"] == "A test project"
        assert result["license"] == "MIT"
        assert result["python_version_preference"] == "3.11"

        mock_get_git_config.assert_has_calls(
            [call("user.name"), call("user.email"), call("user.github")]
        )
        assert mock_prompt.call_count == 6
        mock_confirm.assert_not_called()

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.click.prompt")
    @patch(f"{MODULE_PATH}.click.confirm")
    def test_collects_details_with_warnings_user_proceeds(
        self,
        mock_confirm: MagicMock,
        mock_prompt: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test collecting details when warnings exist and user proceeds."""
        warnings = ["Name too short", "Name invalid"]
        mock_confirm.return_value = True  # User proceeds

        mock_get_git_config.side_effect = [None, None, None]
        mock_prompt.side_effect = [
            "Author From Prompt",  # author_name
            "email@prompt.com",  # author_email
            "gh_user_prompt",  # github_username
            "Desc Prompt",  # project_description
            DEFAULT_LICENSE,  # license
            DEFAULT_PYTHON_VERSION,  # python_version
        ]

        result = collect_project_details(
            self.PROJECT_NAME, name_warnings=warnings, cli_defaults={}
        )

        assert result is not None
        assert result["author_name"] == "Author From Prompt"
        assert result["author_email"] == "email@prompt.com"
        assert result["github_username"] == "gh_user_prompt"
        mock_confirm.assert_called_once_with(
            "Ignore warnings and proceed with this name?", default=True
        )

    @patch(f"{MODULE_PATH}.click.confirm")
    def test_exits_if_user_does_not_proceed_after_warnings(
        self, mock_confirm: MagicMock
    ):
        """Test that function returns empty dict if user chooses not to proceed."""
        warnings = ["Name conflict"]
        mock_confirm.return_value = False  # User does not proceed

        with expect_raise(click.Abort):
            collect_project_details(
                self.PROJECT_NAME, name_warnings=warnings, cli_defaults={}
            )
        mock_confirm.assert_called_once()

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.click.prompt")
    @patch(f"{MODULE_PATH}.click.confirm")
    def test_uses_defaults_when_git_config_missing_and_prompts_return_defaults(
        self,
        mock_confirm: MagicMock,
        mock_prompt: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test defaults used if git config missing & prompts accept defaults."""

        _ = mock_confirm  # avoid unused variable warning

        mock_get_git_config.side_effect = [None, None, None]
        mock_prompt.side_effect = [
            "Default Author",  # author_name
            "default@example.com",  # author_email
            "default_gh",  # github_username
            "Default Description",  # project_description
            DEFAULT_LICENSE,  # license
            DEFAULT_PYTHON_VERSION,  # python_version
        ]

        result = collect_project_details(
            self.PROJECT_NAME, name_warnings=[], cli_defaults={}
        )

        assert result is not None
        assert result["author_name"] == "Default Author"
        assert result["author_email"] == "default@example.com"
        assert result["github_username"] == "default_gh"
        assert result["project_description"] == "Default Description"
        assert result["license"] == DEFAULT_LICENSE
        assert result["python_version_preference"] == DEFAULT_PYTHON_VERSION

        mock_get_git_config.assert_has_calls(
            [call("user.name"), call("user.email"), call("user.github")]
        )
        assert mock_prompt.call_count == 6

    @patch(f"{MODULE_PATH}.get_git_config_value")
    @patch(f"{MODULE_PATH}.click.prompt")
    @patch(f"{MODULE_PATH}.click.confirm")
    def test_cli_defaults_take_precedence(
        self,
        mock_confirm: MagicMock,
        mock_prompt: MagicMock,
        mock_get_git_config: MagicMock,
    ):
        """Test that CLI defaults take precedence over git config values."""

        mock_get_git_config.side_effect = ["Git User", "git@example.com", "gituser"]
        _ = mock_confirm  # avoid unused variable warning

        # Set up CLI defaults
        cli_defaults = {"author_name": "CLI Author", "license": "Apache-2.0"}

        # Set up the mock prompt responses
        mock_prompt.side_effect = [
            "Final Author",
            "final@example.com",
            "final_user",
            "Description",
            "GPL-3.0",
            "3.12",
        ]

        result = collect_project_details(
            self.PROJECT_NAME, name_warnings=[], cli_defaults=cli_defaults
        )

        assert result is not None
        assert result["author_name"] == "Final Author"
        assert result["author_email"] == "final@example.com"
        assert result["github_username"] == "final_user"
        assert result["license"] == "GPL-3.0"

        # Verify the default value in prompt was set correctly
        expected_author_call = call(
            "Author Name",
            default="CLI Author",  # CLI default takes precedence
            show_default=True,
            type=str,
        )
        assert expected_author_call in mock_prompt.mock_calls
