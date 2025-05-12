"""Command-line interface for PyHatchery."""

import os
from typing import Dict, Optional

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
    original_input_name: str, pypi_slug: str, python_slug: str
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
            f"(from input '{original_input_name}') is not PEP 8 compliant: "
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
    author: Optional[str],
    email: Optional[str],
    github_username: Optional[str],
    description: Optional[str],
    license_choice: Optional[str],  # Renamed from license to avoid conflict
    python_version: Optional[str],
    name_warnings: list[str],
    _project_name: str,  # Original project name for context if needed
) -> Dict[str, str] | None:
    """
    Get project details for non-interactive mode, merging CLI args and .env values.

    Args:
        author: Author name from CLI.
        email: Author email from CLI.
        github_username: GitHub username from CLI.
        description: Project description from CLI.
        license_choice: License choice from CLI.
        python_version: Python version from CLI.
        name_warnings: Warnings related to the project name.
        _project_name: The validated project name.

    Returns:
        A dictionary containing project details, or None if required fields are missing.
    """
    if name_warnings:
        click.secho(
            "Warnings were found during project name checks (non-interactive mode):",
            fg="yellow",
            err=True,
        )
        for warning in name_warnings:
            click.secho(f"Warning: {warning}", fg="yellow", err=True)

    env_values = load_from_env()
    details: Dict[str, str] = {}

    field_sources: Dict[str, tuple[Optional[str], Optional[str], Optional[str]]] = {
        "author_name": (author, env_values.get("AUTHOR_NAME"), None),
        "author_email": (email, env_values.get("AUTHOR_EMAIL"), None),
        "github_username": (
            github_username,
            env_values.get("GITHUB_USERNAME"),
            None,
        ),
        "project_description": (
            description,
            env_values.get("PROJECT_DESCRIPTION"),
            None,
        ),
        "license": (license_choice, env_values.get("LICENSE"), DEFAULT_LICENSE),
        "python_version_preference": (
            python_version,
            env_values.get("PYTHON_VERSION"),
            DEFAULT_PYTHON_VERSION,
        ),
    }

    for field, sources in field_sources.items():
        cli_val, env_val, default_val = sources
        if cli_val is not None:
            details[field] = cli_val
        elif env_val is not None:
            details[field] = env_val
        elif default_val is not None:
            details[field] = default_val
        else:
            details[field] = ""  # Ensure key exists even if empty

    missing_fields: list[str] = []
    for field in ["author_name", "author_email"]:
        if not details.get(field):  # Use .get() for safety
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


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(
    __version__,
    "-v",
    "--version",
    prog_name="pyhatchery",
    message="%(prog)s %(version)s",
)
@click.option("--debug", is_flag=True, help="Enable debug mode.")
@click.pass_context
def cli(ctx: click.Context, debug: bool):
    """PyHatchery: A Python project scaffolding tool."""
    try:
        env_debug = str_to_bool(os.environ.get("PYHATCHERY_DEBUG", "false"))
    except ValueError:
        click.secho(
            "Warning: Invalid value for PYHATCHERY_DEBUG environment variable. "
            "Falling back to debug mode being disabled.",
            fg="yellow",
            err=True,
        )
        env_debug = False
    ctx.obj = {"DEBUG": debug or env_debug}


@cli.command("new")
@click.argument("project_name_arg", metavar="PROJECT_NAME")
@click.option(
    "--no-interactive",
    is_flag=True,
    help="Use non-interactive mode (all details provided via flags or .env file).",
)
@click.option("--author", help="Author name for the project.")
@click.option("--email", help="Author email for the project.")
@click.option("--github-username", help="GitHub username for the project.")
@click.option("--description", help="Description of the project.")
@click.option(
    "--license",
    "license_choice",  # Use a different dest name
    type=click.Choice(COMMON_LICENSES),
    default=None,
    help=f"License for the project. Choices: {', '.join(COMMON_LICENSES)}.",
    show_default=f"Defaults to {DEFAULT_LICENSE} if not specified in .env or CLI.",
)
@click.option(
    "--python-version",
    type=click.Choice(PYTHON_VERSIONS),
    default=None,
    help=f"Python version for the project. Choices: {', '.join(PYTHON_VERSIONS)}.",
    show_default=f"Defaults to {DEFAULT_PYTHON_VERSION} "
    "if not specified in .env or CLI.",
)
@click.pass_context
def new(
    ctx: click.Context,
    project_name_arg: str,
    no_interactive: bool,
    author: Optional[str],
    email: Optional[str],
    github_username: Optional[str],
    description: Optional[str],
    license_choice: Optional[str],
    python_version: Optional[str],
):
    """Create a new Python project."""
    debug_flag = ctx.obj.get("DEBUG", False)

    if not project_name_arg:
        click.secho("Error: Project name cannot be empty.", fg="red", err=True)
        return 1

    project_name = project_name_arg

    has_invalid, invalid_error = has_invalid_characters(project_name)
    if has_invalid:
        click.secho(f"Error: {invalid_error}", fg="red", err=True)
        ctx.exit(1)

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
            f"Warning: Project name '{project_name_arg}' normalized to '{pypi_slug}'.",
            fg="yellow",
            err=True,
        )

    current_project_name_for_processing = pypi_slug
    python_slug = derive_python_package_slug(current_project_name_for_processing)

    click.secho(f"Derived PyPI slug: {pypi_slug}", fg="blue", err=True)
    click.secho(f"Derived Python package slug: {python_slug}", fg="blue", err=True)

    name_warnings = _perform_project_name_checks(
        project_name_arg,
        pypi_slug,
        python_slug,
    )

    project_details: Optional[Dict[str, str]] = None
    if no_interactive:
        project_details = _get_project_details_non_interactive(
            author,
            email,
            github_username,
            description,
            license_choice,
            python_version,
            name_warnings,
            current_project_name_for_processing,
        )
    else:
        project_details = collect_project_details(
            current_project_name_for_processing, name_warnings
        )

    if project_details is None:
        ctx.exit(1)

    project_details["project_name_original"] = project_name_arg
    project_details["project_name_normalized"] = current_project_name_for_processing
    project_details["pypi_slug"] = pypi_slug
    project_details["python_package_slug"] = python_slug

    click.secho(
        f"Creating new project: {current_project_name_for_processing}", fg="green"
    )
    if debug_flag:
        debug_display_details = {
            "original_input_name": project_name_arg,
            "name_for_processing": current_project_name_for_processing,
            "pypi_slug": pypi_slug,
            "python_slug": python_slug,
            **project_details,
        }
        click.secho(f"With details: {debug_display_details}", fg="blue")

    click.secho("Project generation logic would run here.", fg="cyan")
    return 0
