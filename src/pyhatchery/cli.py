"""Command-line interface for PyHatchery."""

import dataclasses
import os
from pathlib import Path
from typing import Any, cast

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
from .components.project_generator import create_base_structure
from .utils.config import str_to_bool


@dataclasses.dataclass
class NonInteractiveProjectDetailsArgs:  # pylint: disable=R0902
    """Arguments for non-interactive project detail collection."""

    author: str | None
    email: str | None
    github_username: str | None
    description: str | None
    license_choice: str | None
    python_version: str | None
    name_warnings: list[str]
    project_name: str  # This is the pypi_slug / name_for_processing


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
    args: NonInteractiveProjectDetailsArgs,
) -> dict[str, str] | None:
    """
    Get project details for non-interactive mode, merging CLI args and .env values.

    Args:
        args: Dataclass containing all arguments for non-interactive mode.
              args.project_name here is the pypi_slug.

    Returns:
        A dictionary containing project details, or None if required fields are missing.
    """
    if args.name_warnings:
        click.secho(
            "Warnings were found during project name checks (non-interactive mode):",
            fg="yellow",
            err=True,
        )
        for warning in args.name_warnings:
            click.secho(f"Warning: {warning}", fg="yellow", err=True)

    env_values = load_from_env()
    details: dict[str, str] = {}

    field_definitions: dict[str, tuple[str | None, str, str | None]] = {
        "author_name": (args.author, "AUTHOR_NAME", None),
        "author_email": (args.email, "AUTHOR_EMAIL", None),
        "github_username": (args.github_username, "GITHUB_USERNAME", None),
        "project_description": (args.description, "PROJECT_DESCRIPTION", None),
        "license": (args.license_choice, "LICENSE", DEFAULT_LICENSE),
        "python_version_preference": (
            args.python_version,
            "PYTHON_VERSION",
            DEFAULT_PYTHON_VERSION,
        ),
    }

    for field, (cli_val, env_key, default_val) in field_definitions.items():
        if cli_val is not None:
            details[field] = cli_val
        elif env_values.get(env_key) is not None:
            details[field] = env_values[env_key]
        elif default_val is not None:
            details[field] = default_val
        else:
            details[field] = ""

    missing_fields: list[str] = []
    for field in ["author_name", "author_email"]:
        if not details.get(field):
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


# Public alias for testing purposes to maintain compatibility
def _alias_internal_get_project_details_non_interactive_for_testing(  # pylint: disable=R0913,R0917
    author: str | None,
    email: str | None,
    github_username: str | None,
    description: str | None,
    license_choice: str | None,
    python_version: str | None,
    name_warnings: list[str],
    _project_name: str,  # This is the pypi_slug / name_for_processing
) -> dict[str, str] | None:
    args = NonInteractiveProjectDetailsArgs(
        author=author,
        email=email,
        github_username=github_username,
        description=description,
        license_choice=license_choice,
        python_version=python_version,
        name_warnings=name_warnings,
        project_name=_project_name,
    )
    return _get_project_details_non_interactive(args)


internal_get_project_details_non_interactive_for_testing = (
    _alias_internal_get_project_details_non_interactive_for_testing
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


@dataclasses.dataclass
class NewCommandOptions:
    """Options for the 'new' command, parsed from kwargs."""

    no_interactive: bool
    author: str | None
    email: str | None
    github_username: str | None
    description: str | None
    license_choice: str | None
    python_version: str | None


@dataclasses.dataclass
class ProjectNameDetails:
    """Holds all derived names and warnings for a project."""

    original_arg: str
    pypi_slug: str
    python_slug: str
    name_warnings: list[str]


def _process_project_name(
    project_name_arg: str, ctx: click.Context
) -> ProjectNameDetails | None:
    """Validate and derive all project name variants and warnings."""
    if not project_name_arg:
        click.secho("Error: Project name cannot be empty.", fg="red", err=True)
        ctx.exit(1)  # type: ignore[no-untyped-call]
        return None  # Should not be reached

    has_invalid, invalid_error = has_invalid_characters(project_name_arg)
    if has_invalid:
        click.secho(f"Error: {invalid_error}", fg="red", err=True)
        ctx.exit(1)  # type: ignore[no-untyped-call]
        return None

    pypi_slug = pep503_normalize(project_name_arg)

    is_name_ok, name_error_message = pep503_name_ok(project_name_arg)
    if not is_name_ok:
        click.secho(
            f"Warning: Project name '{project_name_arg}': {name_error_message}",
            fg="yellow",
            err=True,
        )

    if project_name_arg != pypi_slug:
        click.secho(
            f"Warning: Project name '{project_name_arg}' normalized to '{pypi_slug}'.",
            fg="yellow",
            err=True,
        )

    python_slug = derive_python_package_slug(pypi_slug)

    click.secho(f"Derived PyPI slug: {pypi_slug}", fg="blue", err=True)
    click.secho(f"Derived Python package slug: {python_slug}", fg="blue", err=True)

    name_warnings = _perform_project_name_checks(
        project_name_arg,
        pypi_slug,
        python_slug,
    )
    return ProjectNameDetails(
        original_arg=project_name_arg,
        pypi_slug=pypi_slug,
        python_slug=python_slug,
        name_warnings=name_warnings,
    )


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
    "license_choice",
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
    **kwargs: dict[str, Any],
) -> int:  # Added return type hint
    """Create a new Python project."""
    cmd_options = NewCommandOptions(
        no_interactive=cast(bool, kwargs.get("no_interactive", False)),
        author=cast(str | None, kwargs.get("author")),
        email=cast(str | None, kwargs.get("email")),
        github_username=cast(str | None, kwargs.get("github_username")),
        description=cast(str | None, kwargs.get("description")),
        license_choice=cast(str | None, kwargs.get("license_choice")),
        python_version=cast(str | None, kwargs.get("python_version")),
    )
    debug_flag = ctx.obj.get("DEBUG", False)

    name_data = _process_project_name(project_name_arg, ctx)
    if name_data is None:
        return 1

    project_details: dict[str, str] | None
    if cmd_options.no_interactive:
        non_interactive_args = NonInteractiveProjectDetailsArgs(
            author=cmd_options.author,
            email=cmd_options.email,
            github_username=cmd_options.github_username,
            description=cmd_options.description,
            license_choice=cmd_options.license_choice,
            python_version=cmd_options.python_version,
            name_warnings=name_data.name_warnings,
            project_name=name_data.pypi_slug,
        )
        project_details = _get_project_details_non_interactive(non_interactive_args)
    else:
        project_details = collect_project_details(
            name_data.pypi_slug, name_data.name_warnings
        )

    if project_details is None:
        ctx.exit(1)
        return 1

    project_details["project_name_original"] = name_data.original_arg
    project_details["project_name_normalized"] = name_data.pypi_slug
    project_details["pypi_slug"] = name_data.pypi_slug
    project_details["python_package_slug"] = name_data.python_slug

    click.secho(f"Creating new project: {name_data.pypi_slug}", fg="green")
    if debug_flag:
        debug_display_info = {
            "original_input_name": name_data.original_arg,
            "name_for_processing": name_data.pypi_slug,
            "pypi_slug": name_data.pypi_slug,
            "python_slug": name_data.python_slug,
            **project_details,
        }
        click.secho(f"With details: {debug_display_info}", fg="blue")

    try:
        output_path = Path.cwd()
        project_root = create_base_structure(
            output_path,
            project_details["project_name_original"],
            project_details["python_package_slug"],
        )
        click.secho(
            f"Project directory structure created at: {project_root}", fg="green"
        )
    except FileExistsError as e:
        click.secho(f"Error: {str(e)}", fg="red", err=True)
        ctx.exit(1)  # type: ignore[no-untyped-call]
        return 1
    except OSError as e:
        click.secho(
            f"Error creating project directory structure: {str(e)}", fg="red", err=True
        )
        ctx.exit(1)  # type: ignore[no-untyped-call]
        return 1

    return 0
