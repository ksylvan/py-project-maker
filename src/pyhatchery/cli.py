"""Command-line interface for PyHatchery."""

import argparse
import sys

from .__about__ import __version__
from .components.http_client import check_pypi_availability
from .components.name_service import (
    derive_python_package_slug,
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
        print(msg, file=sys.stderr)
    elif is_pypi_taken:
        msg = (
            f"Warning: The name '{pypi_slug}' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        )
        print(msg, file=sys.stderr)

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
        print(warning_msg, file=sys.stderr)


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
            print("Error: Project name cannot be empty.", file=sys.stderr)
            new_parser.print_help(sys.stderr)
            return 1

        project_name = args.project_name

        # Validate the project name itself
        is_name_ok, name_error_message = pep503_name_ok(project_name)
        if not is_name_ok:
            # Special characters like "!" are handled as a hard error
            if "!" in project_name:
                print(name_error_message, file=sys.stderr)
                return 1
            # Other validation failures are just warnings
            print(
                f"Warning: Project name '{project_name}': {name_error_message}",
                file=sys.stderr,
            )

        # Derive slugs
        pypi_slug = pep503_normalize(project_name)
        python_slug = derive_python_package_slug(project_name)

        # Print derived slugs for debugging/info (optional, can be removed later)
        print(f"Derived PyPI slug: {pypi_slug}", file=sys.stderr)
        print(f"Derived Python package slug: {python_slug}", file=sys.stderr)

        # Perform additional name checks and print warnings (non-blocking)
        _perform_project_name_checks(project_name, pypi_slug, python_slug)

        print(f"Creating new project: {project_name}")  # Placeholder
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
