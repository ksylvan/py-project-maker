"""Command-line interface for PyHatchery."""

import argparse
import sys

import click

from .__about__ import __version__
from .components.http_client import check_pypi_availability
from .components.name_service import (
    derive_python_package_slug,
    has_invalid_characters,
    is_valid_python_package_name,
    pep503_name_ok,  # Keep this for the initial project name check
    pep503_normalize,
)


def _perform_project_name_checks(
    project_name: str, pypi_slug: str, python_slug: str
) -> None:
    """Helper to perform and print warnings for project name checks."""
    # Note: We don't check pep503_name_ok here, as it's done earlier as a blocking check

    # Check PyPI availability
    is_pypi_taken, pypi_error_msg = check_pypi_availability(pypi_slug)
    if pypi_error_msg:
        msg = (
            f"Warning: PyPI availability check for '{pypi_slug}' failed: "
            f"{pypi_error_msg}"
        )
        click.secho(msg, fg="yellow", err=True)
    elif is_pypi_taken:
        msg = (
            f"Warning: The name '{pypi_slug}' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        )
        click.secho(msg, fg="yellow", err=True)

    # Check Python package slug PEP 8 compliance
    is_python_slug_valid, python_slug_error_msg = is_valid_python_package_name(
        python_slug
    )
    if not is_python_slug_valid:
        warning_msg = (
            f"Warning: Derived Python package name '{python_slug}' "
            f"(from input '{project_name}') is not PEP 8 compliant: "
            f"{python_slug_error_msg}"
        )
        click.secho(warning_msg, fg="yellow", err=True)


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
        prog="pyhatchery",  # Set program name for help messages
        description="PyHatchery: A Python project scaffolding tool.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"pyhatchery {__version__}",
        help="Show the version and exit.",
    )
    # Subparsers for commands like "new"
    subparsers = parser.add_subparsers(
        dest="command", title="Commands", help="Available commands"
    )

    # "new" command parser
    new_parser = subparsers.add_parser("new", help="Create a new Python project.")
    new_parser.add_argument("project_name", help="The name of the project to create.")

    args = parser.parse_args(argv if argv is not None else sys.argv[1:])

    if args.command == "new":
        if not args.project_name:  # Basic check, more robust validation later
            # argparse usually handles missing required arguments,
            # but this is a fallback.
            # For a missing positional argument, argparse will exit before this.
            # This explicit check is more for an empty string if argparse allows it.
            click.secho("Error: Project name cannot be empty.", fg="red", err=True)
            new_parser.print_help(sys.stderr)
            return 1

        original_name = args.project_name

        # First check for invalid characters that should cause immediate rejection
        has_invalid, invalid_error = has_invalid_characters(original_name)
        if has_invalid:
            click.secho(f"Error: {invalid_error}", fg="red", err=True)
            return 1

        # Now derive slugs
        pypi_slug = pep503_normalize(original_name)

        # Check original name format for PEP503 compliance (for warnings)
        is_name_ok, name_error_message = pep503_name_ok(original_name)
        if not is_name_ok:
            # Other validation failures are just warnings
            click.secho(
                f"Warning: Project name '{original_name}': {name_error_message}",
                fg="yellow",
                err=True,
            )

        # Warn about normalization if needed
        if original_name != pypi_slug:
            click.secho(
                f"Warning: Project name '{original_name}' normalized to '{pypi_slug}'.",
                fg="yellow",
                err=True,
            )

        # Use normalized name for internal operations
        project_name = pypi_slug
        python_slug = derive_python_package_slug(project_name)

        # Print derived slugs for debugging/info (optional, can be removed later)
        click.secho(f"Derived PyPI slug: {pypi_slug}", fg="blue", err=True)
        click.secho(f"Derived Python package slug: {python_slug}", fg="blue", err=True)

        # Perform additional name checks and print warnings (non-blocking)
        _perform_project_name_checks(project_name, pypi_slug, python_slug)

        click.secho(f"Creating new project: {project_name}", fg="green")
        # Actual project creation logic will go here later.
        return 0

    # If execution reaches here, args.command was not "new".
    # Check if it was None (meaning no command was provided).
    if args.command is None:
        # No command was provided
        parser.print_help(sys.stderr)
        return 1

    # Should not be reached if subparsers are set up correctly
    return 1


if __name__ == "__main__":
    sys.exit(main())
