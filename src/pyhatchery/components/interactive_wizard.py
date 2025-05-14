"""
Component responsible for guiding the user through an interactive wizard
to gather project details.
"""

import click

from pyhatchery.components.config_loader import get_git_config_value

COMMON_LICENSES: list[str] = ["MIT", "Apache-2.0", "GPL-3.0"]
PYTHON_VERSIONS: list[str] = ["3.10", "3.11", "3.12"]
DEFAULT_PYTHON_VERSION: str = "3.11"
DEFAULT_LICENSE: str = "MIT"


def collect_project_details(
    project_name: str,
    name_warnings: list[str],
    cli_defaults: dict[str, str] | None = None,
) -> dict[str, str]:
    """
    Collect project details interactively.

    Args:
        project_name: The normalized project name
        name_warnings: List of warnings from name validation
        cli_defaults: Dictionary of default values provided via CLI arguments

    Returns:
        Dictionary of project details or throws a click.Abort exception
        (for example, if user cancels or performs a keyboard interrupt)
    """
    cli_defaults = cli_defaults or {}

    # Display header
    click.secho("-" * 30, fg="blue")
    click.secho(f"Configuring project: {project_name}", fg="blue")
    click.secho("-" * 30, fg="blue")

    # If there are name warnings, confirm proceeding
    try:
        if name_warnings:
            proceed = click.confirm(
                "Ignore warnings and proceed with this name?", default=True
            )
            if not proceed:
                click.secho("Process cancelled by user.", fg="red")
                raise click.Abort()

        # Get author details with CLI arguments taking precedence
        author_name = click.prompt(
            "Author Name",
            default=cli_defaults.get("author_name", get_git_config_value("user.name")),
            show_default=True,
            type=str,
        )

        author_email = click.prompt(
            "Author Email",
            default=cli_defaults.get(
                "author_email", get_git_config_value("user.email")
            ),
            show_default=True,
            type=str,
        )

        github_username = click.prompt(
            "GitHub Username",
            default=cli_defaults.get(
                "github_username", get_git_config_value("user.github")
            ),
            type=str,
            show_default=True,
        )

        # Get other project details with CLI arguments taking precedence
        project_description = click.prompt(
            "Project Description",
            default=cli_defaults.get("project_description", ""),
            type=str,
            show_default=True,
        )

        license_choice = click.prompt(
            "License",
            default=cli_defaults.get("license", DEFAULT_LICENSE),
            type=click.Choice(COMMON_LICENSES),
            show_choices=True,
            show_default=True,
        )

        python_version = click.prompt(
            "Python Version",
            default=cli_defaults.get(
                "python_version_preference", DEFAULT_PYTHON_VERSION
            ),
            type=click.Choice(PYTHON_VERSIONS),
            show_choices=True,
            show_default=True,
        )
    except (click.Abort, KeyboardInterrupt) as e:
        click.secho("\nProcess cancelled by user.", fg="red")
        raise click.Abort() from e

    # Return collected details
    return {
        "author_name": author_name,
        "author_email": author_email,
        "github_username": github_username,
        "project_description": project_description,
        "license": license_choice,
        "python_version_preference": python_version,
    }
