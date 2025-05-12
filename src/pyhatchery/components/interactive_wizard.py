"""
Component responsible for guiding the user through an interactive wizard
to gather project details.
"""

from typing import Dict, List

import click

from pyhatchery.components.config_loader import get_git_config_value

COMMON_LICENSES: List[str] = ["MIT", "Apache-2.0", "GPL-3.0"]
PYTHON_VERSIONS: List[str] = ["3.10", "3.11", "3.12"]
DEFAULT_PYTHON_VERSION: str = "3.11"
DEFAULT_LICENSE: str = "MIT"


def prompt_for_value(
    prompt_message: str, default_value: str | None = None, max_retries: int = 3
) -> str | None:
    """Helper function to prompt user for input with a default."""
    if default_value is not None:
        prompt_with_default = f"{prompt_message} (default: {default_value}): "
        user_input = input(prompt_with_default).strip()
        if user_input:
            return user_input
        return default_value

    prompt_no_default = f"{prompt_message}: "
    retries = 0
    while retries < max_retries:
        user_input = input(prompt_no_default).strip()
        if user_input:
            return user_input
        click.secho("This field cannot be empty.", fg="red")
        retries += 1

    raise ValueError(
        f"Maximum retry limit ({max_retries}) reached. No valid input provided."
    )


def prompt_for_choice(
    prompt_message: str, choices: List[str], default_choice: str, max_retries: int = 3
) -> str | None:
    "Helper function to prompt user to select from choices with retry limit."
    click.secho(prompt_message, fg="cyan")
    for i, choice in enumerate(choices):
        if choice == default_choice:
            click.secho(f"  {i + 1}. {choice}", fg="green", bold=True, nl=False)
            click.secho(" (default)", fg="green")
        else:
            click.secho(f"  {i + 1}. {choice}")

    retries = 0
    while retries < max_retries:
        try:
            raw_selection = input(
                f"Enter your choice (1-{len(choices)}, default is {default_choice}): "
            ).strip()
            if not raw_selection:
                return default_choice
            selection = int(raw_selection)
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            message = f"Invalid choice. Enter a number from 1 to {len(choices)}."
            click.secho(message, fg="red")
        except ValueError:
            click.secho("Invalid input. Please enter a number.", fg="red")
    raise ValueError(
        f"Maximum retry limit ({max_retries}) reached. No valid input provided."
    )


def collect_project_details(
    project_name: str,
    name_warnings: list[str] | None,
) -> Dict[str, str] | None:
    """
    Collects project details from the user via an interactive wizard.

    Args:
        project_name: The name of the project.
        name_warnings: A list of warnings related to the project name from Story 1.1A.

    Returns:
        A dictionary containing the collected project details, or None if the user
        chooses not to proceed after warnings.
    """
    click.secho("-" * 30, fg="blue")
    click.secho(f"Configuring project: {project_name}", fg="blue", bold=True)
    click.secho("-" * 30, fg="blue")

    if name_warnings:
        proceed_prompt = (
            "Ignore warnings and proceed with this name? (yes/no, default: yes): "
        )
        proceed = input(proceed_prompt).strip().lower()
        if proceed in {"no", "n"}:
            click.secho("Exiting project generation.", fg="red")
            return None
        click.secho("-" * 30, fg="blue")

    author_name_default = get_git_config_value("user.name")
    author_email_default = get_git_config_value("user.email")

    details: Dict[str, str] = {}

    try:
        details["author_name"] = (
            prompt_for_value("Author Name", author_name_default) or ""
        )
        details["author_email"] = (
            prompt_for_value("Author Email", author_email_default) or ""
        )
        details["github_username"] = prompt_for_value("GitHub Username") or ""
        details["project_description"] = prompt_for_value("Project Description") or ""
        details["license"] = (
            prompt_for_choice("Select License:", COMMON_LICENSES, DEFAULT_LICENSE) or ""
        )
        details["python_version_preference"] = (
            prompt_for_choice(
                "Select Python Version:", PYTHON_VERSIONS, DEFAULT_PYTHON_VERSION
            )
            or ""
        )

    except ValueError as e:
        click.secho(f"Error: {e}", fg="red", bold=True)
        click.secho("Exiting project generation.", fg="red")
        return None
    except KeyboardInterrupt:
        click.secho("\nUser interrupted the process.", fg="yellow")
        return None
    except EOFError:
        click.secho("\nEnd of file reached. Exiting.", fg="yellow")
        return None

    click.secho("-" * 30, fg="blue")
    click.secho("Project details collected.", fg="green", bold=True)
    return details


if __name__ == "__main__":
    click.secho("Testing Interactive Wizard...", fg="magenta", bold=True)
    test_warnings = [
        "The name 'Test-Project' might already be taken on PyPI.",
        "Derived Python package name 'Test_Project' does not follow PEP 8.",
    ]
    collected_info = collect_project_details(
        "My Test Project", name_warnings=test_warnings
    )
    if collected_info:
        click.secho("\nCollected Information:", fg="magenta", bold=True)
        for key, value in collected_info.items():
            click.secho(f"  {key}: {value}", fg="magenta")

    click.secho(
        "\nTesting Interactive Wizard (no warnings)...", fg="magenta", bold=True
    )
    collected_info_no_warn = collect_project_details("Another Project", [])
    if collected_info_no_warn:
        click.secho("\nCollected Information (no warnings):", fg="magenta", bold=True)
        for key, value in collected_info_no_warn.items():
            click.secho(f"  {key}: {value}", fg="magenta")
