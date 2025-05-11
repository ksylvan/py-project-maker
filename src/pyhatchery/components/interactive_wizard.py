"""
Component responsible for guiding the user through an interactive wizard
to gather project details.
"""

from typing import Dict, List, Optional

from pyhatchery.components.config_loader import get_git_config_value

# Predefined choices for license and Python versions
COMMON_LICENSES: List[str] = ["MIT", "Apache-2.0", "GPL-3.0"]
PYTHON_VERSIONS: List[str] = ["3.10", "3.11", "3.12"]
DEFAULT_PYTHON_VERSION: str = "3.11"
DEFAULT_LICENSE: str = "MIT"


def prompt_for_value(prompt_message: str, default_value: Optional[str] = None) -> str:
    """Helper function to prompt user for input with a default."""
    if default_value:
        prompt_with_default = f"{prompt_message} (default: {default_value}): "
        user_input = input(prompt_with_default).strip()
        if user_input:
            return user_input
        return default_value

    prompt_no_default = f"{prompt_message}: "
    while True:
        user_input = input(prompt_no_default).strip()
        if user_input:
            return user_input
        print("This field cannot be empty.")


def prompt_for_choice(
    prompt_message: str, choices: List[str], default_choice: str
) -> str:
    """Helper function to prompt user to select from a list of choices."""
    print(prompt_message)
    for i, choice in enumerate(choices):
        print(f"  {i + 1}. {choice}{' (default)' if choice == default_choice else ''}")

    while True:
        try:
            raw_selection = input(
                f"Enter your choice (1-{len(choices)}, default is {default_choice}): "
            ).strip()
            if not raw_selection:  # User pressed Enter, accept default
                return default_choice
            selection = int(raw_selection)
            if 1 <= selection <= len(choices):
                return choices[selection - 1]
            print(  # De-indented from else
                f"Invalid choice. Enter a number from 1 to {len(choices)}."
            )
        except ValueError:
            print("Invalid input. Please enter a number.")


def collect_project_details(
    project_name: str, name_warnings: Optional[List[str]] = None
) -> Optional[Dict[str, str]]:
    """
    Collects project details from the user via an interactive wizard.

    Args:
        project_name: The name of the project.
        name_warnings: A list of warnings related to the project name from Story 1.1A.

    Returns:
        A dictionary containing the collected project details, or None if the user
        chooses not to proceed after warnings.
    """
    print("-" * 30)
    print(f"Configuring project: {project_name}")
    print("-" * 30)

    if name_warnings:
        print("\nProject Name Warnings:")
        for warning in name_warnings:
            print(f"  - {warning}")
        proceed_prompt = "Proceed with this name? (yes/no, default: yes): "
        proceed = input(proceed_prompt).strip().lower()
        if proceed == "no":
            print("Exiting project generation.")
            return None
        print("-" * 30)  # Separator after handling warnings

    author_name_default = get_git_config_value("user.name")
    author_email_default = get_git_config_value("user.email")

    details: Dict[str, str] = {}

    details["author_name"] = prompt_for_value("Author Name", author_name_default)
    details["author_email"] = prompt_for_value("Author Email", author_email_default)
    details["github_username"] = prompt_for_value("GitHub Username")
    details["project_description"] = prompt_for_value("Project Description")

    details["license"] = prompt_for_choice(
        "Select License:", COMMON_LICENSES, DEFAULT_LICENSE
    )
    details["python_version_preference"] = prompt_for_choice(
        "Select Python Version:", PYTHON_VERSIONS, DEFAULT_PYTHON_VERSION
    )

    print("-" * 30)
    print("Project details collected.")
    return details


if __name__ == "__main__":
    # Example usage for testing the wizard directly
    print("Testing Interactive Wizard...")
    # Simulate some name warnings
    test_warnings = [
        "The name 'Test-Project' might already be taken on PyPI.",
        "Derived Python package name 'Test_Project' does not follow PEP 8.",
    ]
    collected_info = collect_project_details(
        "My Test Project", name_warnings=test_warnings
    )
    if collected_info:
        print("\nCollected Information:")
        for key, value in collected_info.items():
            print(f"  {key}: {value}")

    print("\nTesting Interactive Wizard (no warnings)...")
    collected_info_no_warn = collect_project_details("Another Project")
    if collected_info_no_warn:
        print("\nCollected Information (no warnings):")
        for key, value in collected_info_no_warn.items():
            print(f"  {key}: {value}")
