"""Command-line interface for PyHatchery."""

import argparse
import sys

from .__about__ import __version__
from .components.name_service import pep503_name_ok


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

        # Validate the project name using a helper function
        is_valid, error_message = pep503_name_ok(args.project_name)
        if not is_valid:
            print(error_message, file=sys.stderr)
            return 1

        print(f"Creating new project: {args.project_name}")  # Placeholder for AC1 & AC4
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
