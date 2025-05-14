"""Command-line interface for PyHatchery."""

import os
from dataclasses import dataclass, field
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
from .components.project_generator import create_base_structure, setup_project_directory
from .utils.config import str_to_bool


@dataclass
class ProjectAuthorDetails:
    """Holds author details for a project."""

    name: str | None = None
    email: str | None = None
    github_username: str | None = None


@dataclass
class ProjectNameDetails:
    """Holds all derived names and warnings for a project."""

    original_arg: str
    pypi_slug: str
    python_slug: str
    name_warnings: list[str]


@dataclass
class ProjectOptions:
    """Options for project creation."""

    no_interactive: bool = False
    author: ProjectAuthorDetails = field(default_factory=ProjectAuthorDetails)
    description: str | None = None
    license_choice: str | None = None
    python_version: str | None = None
    name_warnings: list[str] = field(default_factory=lambda: [])
    project_name: str | None = None
    output_dir: Path | None = None  # Added for custom output location


def display_warning(message: str) -> None:
    """Display a warning message."""
    click.secho(f"Warning: {message}", fg="yellow", err=True)


def display_error(message: str) -> None:
    """Display an error message."""
    click.secho(f"Error: {message}", fg="red", err=True)


def validate_project_name(project_name: str, ctx: click.Context) -> ProjectNameDetails:
    """Validate and process the project name."""
    if not project_name:
        display_error("Project name cannot be empty.")
        ctx.exit(1)

    has_invalid, invalid_error = has_invalid_characters(project_name)
    if has_invalid:
        display_error(invalid_error)
        ctx.exit(1)

    pypi_slug = pep503_normalize(project_name)
    python_slug = derive_python_package_slug(pypi_slug)

    warnings: list[str] = []

    # Check if name is PEP-compliant
    is_name_ok, name_error_message = pep503_name_ok(project_name)
    if not is_name_ok:
        warnings.append(f"Project name '{project_name}': {name_error_message}")

    # Notify if name was normalized
    if project_name != pypi_slug:
        warnings.append(f"Project name '{project_name}' normalized to '{pypi_slug}'.")

    # Display derived names
    click.secho(f"Derived PyPI slug: {pypi_slug}", fg="blue", err=True)
    click.secho(f"Derived Python package slug: {python_slug}", fg="blue", err=True)

    # Show any warnings
    for warning in warnings:
        display_warning(warning)

    # Check PyPI availability and Python package validity
    name_warnings = check_name_validity(project_name, pypi_slug, python_slug)

    return ProjectNameDetails(
        original_arg=project_name,
        pypi_slug=pypi_slug,
        python_slug=python_slug,
        name_warnings=name_warnings,
    )


def check_name_validity(
    original_name: str, pypi_slug: str, python_slug: str
) -> list[str]:
    """Check PyPI availability and Python package name validity."""
    warnings: list[str] = []

    # Check PyPI availability
    is_pypi_taken, pypi_error_msg = check_pypi_availability(pypi_slug)
    if pypi_error_msg:
        warnings.append(
            f"PyPI availability check for '{pypi_slug}' failed: {pypi_error_msg}"
        )
    elif is_pypi_taken:
        warnings.append(
            f"The name '{pypi_slug}' might already be taken on PyPI. "
            "You may want to choose a different name if you plan to publish "
            "this package publicly."
        )

    # Check Python package name validity
    is_python_slug_valid, python_slug_error_msg = is_valid_python_package_name(
        python_slug
    )
    if not is_python_slug_valid:
        warnings.append(
            f"Derived Python package name '{python_slug}' "
            f"(from input '{original_name}') is not PEP 8 compliant: "
            f"{python_slug_error_msg}"
        )

    if warnings:
        click.secho(
            "Problems were found during project name checks. "
            "You can choose to proceed or cancel.",
            fg="yellow",
            err=True,
        )
        for warning in warnings:
            display_warning(warning)

    return warnings


def get_project_details(options: ProjectOptions) -> dict[str, str] | None:
    """Get project details either interactively or non-interactively."""

    if options.no_interactive:
        return get_non_interactive_details(options)

    # Create a dictionary of default values from CLI options
    defaults: dict[str, str] = {}

    if options.author.name:
        defaults["author_name"] = options.author.name
    if options.author.email:
        defaults["author_email"] = options.author.email
    if options.author.github_username:
        defaults["github_username"] = options.author.github_username
    if options.description:
        defaults["project_description"] = options.description
    if options.license_choice:
        defaults["license"] = options.license_choice
    if options.python_version:
        defaults["python_version_preference"] = options.python_version

    return collect_project_details(
        cast(str, options.project_name), options.name_warnings, defaults
    )


def get_non_interactive_details(options: ProjectOptions) -> dict[str, str] | None:
    """Get project details in non-interactive mode."""
    env_values = load_from_env()
    details: dict[str, str] = {}

    # Define fields with their sources (CLI, env, default)
    field_map: dict[str, tuple[str | None, str, str | None]] = {
        "author_name": (options.author.name, "AUTHOR_NAME", None),
        "author_email": (options.author.email, "AUTHOR_EMAIL", None),
        "github_username": (options.author.github_username, "GITHUB_USERNAME", ""),
        "project_description": (options.description, "PROJECT_DESCRIPTION", ""),
        "license": (options.license_choice, "LICENSE", DEFAULT_LICENSE),
        "python_version_preference": (
            options.python_version,
            "PYTHON_VERSION",
            DEFAULT_PYTHON_VERSION,
        ),
    }

    # Populate details from available sources
    for f, (cli_val, env_key, default_val) in field_map.items():
        if cli_val is not None:
            details[f] = cli_val
        elif env_values.get(env_key) is not None:
            details[f] = env_values[env_key]
        elif default_val is not None:
            details[f] = default_val

    # Check for required fields
    missing_fields = [
        field for field in ["author_name", "author_email"] if not details.get(field)
    ]

    if missing_fields:
        display_error(
            "The following required fields are missing in non-interactive mode:"
        )
        for f in missing_fields:
            click.secho(f"  - {f}", fg="red", err=True)
        click.secho(
            "Please provide these values via CLI flags or .env file.",
            fg="red",
            err=True,
        )
        return None

    return details


def create_project(
    name_data: ProjectNameDetails,
    project_details: dict[str, str],
    output_dir: Path | None,  # Added for custom output location
    debug: bool,
) -> int:
    """Create the project structure."""
    # Add name details to project details
    project_details.update(
        {
            "project_name_original": name_data.original_arg,
            "project_name_normalized": name_data.pypi_slug,
            "pypi_slug": name_data.pypi_slug,
            "python_package_slug": name_data.python_slug,
        }
    )

    click.secho(f"Creating new project: {name_data.pypi_slug}", fg="green")

    if debug:
        debug_info = {
            "original_input_name": name_data.original_arg,
            "name_for_processing": name_data.pypi_slug,
            "pypi_slug": name_data.pypi_slug,
            "python_slug": name_data.python_slug,
            **project_details,
        }
        click.secho(f"With details: {debug_info}", fg="blue")

    try:
        base_output_dir = output_dir if output_dir else Path.cwd()

        actual_project_root_path = setup_project_directory(
            base_output_dir,
            project_details["project_name_original"],
        )

        create_base_structure(
            actual_project_root_path,
            project_details["python_package_slug"],
            project_details["project_name_original"],  # Pass original name for README
        )
        click.secho(
            f"Project directory structure created at: {actual_project_root_path}",
            fg="green",
        )
        return 0
    except FileExistsError as e:
        display_error(str(e))
        return 1
    except OSError as e:
        display_error(f"Error creating project directory structure: {str(e)}")
        return 1


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
        display_warning(
            "Invalid value for PYHATCHERY_DEBUG environment variable. "
            "Falling back to debug mode being disabled."
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
@click.option(
    "-o",
    "--output-dir",
    "output_dir_cli",  # Use a different dest to avoid conflict with existing var name
    default=None,
    help="Output directory for the project.",
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True),
)
@click.pass_context
def new(ctx: click.Context, project_name_arg: str, **kwargs: Any) -> int:
    """Create a new Python project."""
    # Create author details from kwargs
    author_details = ProjectAuthorDetails(
        name=cast(str | None, kwargs.get("author")),
        email=cast(str | None, kwargs.get("email")),
        github_username=cast(str | None, kwargs.get("github_username")),
    )

    # Create options object from kwargs
    options = ProjectOptions(
        no_interactive=cast(bool, kwargs.get("no_interactive", False)),
        author=author_details,
        description=cast(str | None, kwargs.get("description")),
        license_choice=cast(str | None, kwargs.get("license_choice")),
        python_version=cast(str | None, kwargs.get("python_version")),
        output_dir=Path(kwargs["output_dir_cli"])
        if kwargs.get("output_dir_cli")
        else None,
    )

    debug_flag = ctx.obj.get("DEBUG", False)

    # Validate and process project name
    name_data = validate_project_name(project_name_arg, ctx)

    # Set project name in options
    options.project_name = name_data.pypi_slug
    options.name_warnings = name_data.name_warnings

    # Get project details
    try:
        project_details = get_project_details(options)
    except click.Abort:
        ctx.exit(1)
    if project_details is None:
        ctx.exit(1)

    # Create the project
    if create_project(name_data, project_details, options.output_dir, debug_flag):
        ctx.exit(1)
    click.secho(f"Project created successfully: {name_data.pypi_slug}", fg="green")
    return 0
