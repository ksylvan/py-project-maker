"""Command-line interface for PyHatchery."""

import argparse
import os
import sys
from typing import Dict

import click

from . import __version__
from .components.config_loader import load_from_env
from .components.http_client import check_pypi_availability
from .components.interactive_wizard import (
    COMMON_LICENSES,
    DEFAULT_LICENSE,
    DEFAULT_PYTHON_VERSION,
    PYTHON_VERSIONS,
    collect_project_details,
)
from .components.name_service import (
    derive_python_package_slug,
    has_invalid_characters,
    is_valid_python_package_name,
    pep503_name_ok,
    pep503_normalize,
)
from .utils.config import str_to_bool


def _perform_project_name_checks(
    project_name: str, pypi_slug: str, python_slug: str
) -> list[str]:
    """
    Helper to perform and print warnings for project name checks.
    Returns a list of warning messages.
    """
    warnings: list[str] = []

    is_pypi_taken, pypi_error_msg = check_pypi_availability(pypi_slug)
    if pypi_error_msg:
        msg = f"PyPI availability check for '{pypi_slug}' failed: {pypi_error_msg}"
        warnings.append(msg)
    elif is_pypi_taken:
        msg = (
            f"The name '{pypi_slug}' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        )
        warnings.append(msg)

    is_python_slug_valid, python_slug_error_msg = is_valid_python_package_name(
        python_slug
    )
    if not is_python_slug_valid:
        warning_msg = (
            f"Derived Python package name '{python_slug}' "
            f"(from input '{project_name}') is not PEP 8 compliant: "
            f"{python_slug_error_msg}"
        )
        warnings.append(warning_msg)

    if warnings:
        click.secho(
            "Problems were found during project name checks. "
            "You can choose to proceed or cancel.",
            fg="yellow",
            err=True,
        )
        for _w in warnings:
            click.secho(f"Warning: {_w}", fg="yellow", err=True)

    return warnings


def _get_project_details_non_interactive(
    args: argparse.Namespace, name_warnings: list[str], _project_name: str
) -> Dict[str, str] | None:
    """
    Get project details for non-interactive mode, merging CLI args and .env values.

    Args:
        args: The command-line arguments.
        name_warnings: Warnings related to the project name.
        project_name: The validated project name.

    Returns:
        A dictionary containing project details, or None if required fields are missing.
    """
    # Display warnings but don't prompt for re-entry in non-interactive mode
    if name_warnings:
        click.secho(
            "Warnings were found during project name checks (non-interactive mode):",
            fg="yellow",
            err=True,
        )
        for warning in name_warnings:
            click.secho(f"Warning: {warning}", fg="yellow", err=True)

    # Load from .env file if it exists
    env_values = load_from_env()

    # Merge sources with correct precedence: CLI args > .env > defaults
    details: Dict[str, str] = {}

    # Define required fields and their sources
    field_sources: Dict[str, tuple[str | None, str | None, str | None]] = {
        "author_name": (args.author, env_values.get("AUTHOR_NAME"), None),
        "author_email": (args.email, env_values.get("AUTHOR_EMAIL"), None),
        "github_username": (
            args.github_username,
            env_values.get("GITHUB_USERNAME"),
            None,
        ),
        "project_description": (
            args.description,
            env_values.get("PROJECT_DESCRIPTION"),
            None,
        ),
        "license": (args.license, env_values.get("LICENSE"), DEFAULT_LICENSE),
        "python_version_preference": (
            args.python_version,
            env_values.get("PYTHON_VERSION"),
            DEFAULT_PYTHON_VERSION,
        ),
    }

    # Merge sources with correct precedence
    for field, sources in field_sources.items():
        cli_value, env_value, default_value = sources
        # CLI arguments take the highest precedence
        if cli_value is not None:
            details[field] = cli_value
        # If no CLI argument is provided, use the value from the .env file
        elif env_value is not None:
            details[field] = env_value
        # If neither CLI argument nor .env value is provided, use the default value
        elif default_value is not None:
            details[field] = default_value
        # If all sources are missing, set the field to an empty string
        else:
            details[field] = ""

    # Check for missing required fields (author_name and author_email are required)
    missing_fields: list[str] = []
    for field in ["author_name", "author_email"]:
        if not details[field]:
            missing_fields.append(field)

    if missing_fields:
        click.secho(
            "Error: The following required fields are missing in non-interactive mode:",
            fg="red",
            err=True,
        )
        for field in missing_fields:
            click.secho(f"  - {field}", fg="red", err=True)
        click.secho(
            "Please provide these values via CLI flags or .env file.",
            fg="red",
            err=True,
        )
        return None

    return details


# Public alias for testing purposes
internal_get_project_details_non_interactive_for_testing = (
    _get_project_details_non_interactive
)


def _handle_new_command(
    args: argparse.Namespace, new_parser: argparse.ArgumentParser, debug_flag: bool
) -> int:
    """Handles the 'new' command logic."""
    if not args.project_name:
        click.secho("Error: Project name cannot be empty.", fg="red", err=True)
        new_parser.print_help(sys.stderr)
        return 1

    project_name = args.project_name

    has_invalid, invalid_error = has_invalid_characters(project_name)
    if has_invalid:
        click.secho(f"Error: {invalid_error}", fg="red", err=True)
        return 1

    pypi_slug = pep503_normalize(project_name)

    is_name_ok, name_error_message = pep503_name_ok(project_name)
    if not is_name_ok:
        click.secho(
            f"Warning: Project name '{project_name}': {name_error_message}",
            fg="yellow",
            err=True,
        )

    if project_name != pypi_slug:
        click.secho(
            f"Warning: Project name '{project_name}' normalized to '{pypi_slug}'.",
            fg="yellow",
            err=True,
        )

    project_name = pypi_slug
    python_slug = derive_python_package_slug(project_name)

    click.secho(f"Derived PyPI slug: {pypi_slug}", fg="blue", err=True)
    click.secho(f"Derived Python package slug: {python_slug}", fg="blue", err=True)

    name_warnings = _perform_project_name_checks(project_name, pypi_slug, python_slug)

    # Handle interactive vs. non-interactive mode
    if args.no_interactive:
        project_details = _get_project_details_non_interactive(
            args, name_warnings, project_name
        )
    else:
        project_details = collect_project_details(project_name, name_warnings)

    if project_details is None:
        return 1

    click.secho(f"Creating new project: {project_name}", fg="green")
    if debug_flag:
        click.secho(f"With details: {project_details}", fg="blue")

    return 0


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the PyHatchery CLI.

    Args:
        argv: Command-line arguments. Defaults to None,
              which means sys.argv[1:] will be used.

    Returns:
        Exit code for the process.
    """
    parser = argparse.ArgumentParser(
        prog="pyhatchery",
        description="PyHatchery: A Python project scaffolding tool.",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"pyhatchery {__version__}",
        help="Show the version and exit.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode.",
    )
    subparsers = parser.add_subparsers(
        dest="command", title="Commands", help="Available commands"
    )

    # Configure the 'new' command with additional flags for non-interactive mode
    new_parser = subparsers.add_parser(
        "new",
        help="Create a new Python project.",
        usage="pyhatchery new [-h] project_name",
    )
    new_parser.add_argument("project_name", help="The name of the project to create.")
    new_parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Use non-interactive mode (all details provided via flags or .env file).",
    )
    new_parser.add_argument(
        "--author",
        help="Author name for the project.",
    )
    new_parser.add_argument(
        "--email",
        help="Author email for the project.",
    )
    new_parser.add_argument(
        "--github-username",
        help="GitHub username for the project.",
    )
    new_parser.add_argument(
        "--description",
        help="Description of the project.",
    )
    new_parser.add_argument(
        "--license",
        choices=COMMON_LICENSES,
        default=None,  # So it can be differentiated from not provided
        help=f"License for the project. Choices: {', '.join(COMMON_LICENSES)}.",
    )
    new_parser.add_argument(
        "--python-version",
        choices=PYTHON_VERSIONS,
        default=None,  # So it can be differentiated from not provided
        help=f"Python version for the project. Choices: {', '.join(PYTHON_VERSIONS)}.",
    )

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    try:
        debug_flag = str_to_bool(os.environ.get("PYHATCHERY_DEBUG", None)) or args.debug
    except ValueError:
        click.secho(
            "Warning: Invalid value for PYHATCHERY_DEBUG environment variable. "
            "Falling back to debug mode being disabled.",
            fg="yellow",
            err=True,
        )
        debug_flag = args.debug
    if args.command == "new":
        return _handle_new_command(args, new_parser, debug_flag)

    if args.command is None:
        parser.print_help(sys.stderr)
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
