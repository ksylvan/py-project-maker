"""Command-line interface for PyHatchery."""

import argparse
import os
import sys

import click

from . import __version__
from .components.http_client import check_pypi_availability
from .components.interactive_wizard import collect_project_details
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

    # TODO: Add --no-interactive flag check here later (Story 1.3)
    # Look in ai/stories/01.03.story.md

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

    new_parser = subparsers.add_parser("new", help="Create a new Python project.")
    new_parser.add_argument("project_name", help="The name of the project to create.")

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
