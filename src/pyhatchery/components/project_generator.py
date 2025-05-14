"""Project generator component for PyHatchery.

This module handles the creation of the basic directory structure for new projects.
"""

import logging
from pathlib import Path
from typing import Any

import click

# Define a more specific type for the structure if possible,
# for now, dict[str, Any] or dict[str, dict[str, str]] might be suitable.
DEFAULT_PROJECT_STRUCTURE: dict[str, Any] = {
    "dirs": ["src/{python_package_slug}", "tests", "docs"],
    "files": {
        "src/{python_package_slug}/__init__.py": "",
        "tests/__init__.py": "",
        "README.md": (
            "# {project_name}\\n\\nThis project was generated with PyHatchery."
        ),
        ".gitignore": "*.pyc\\n__pycache__/\\n.env\\n",
    },
}

logger = logging.getLogger(__name__)


def setup_project_directory(base_output_dir: Path, project_name_original: str) -> Path:
    """
    Sets up the project directory.

    Args:
        base_output_dir: The base directory where the project will be created.
        project_name_original: The original name of the project.

    Returns:
        The path to the created project root directory.

    Raises:
        FileExistsError: If the target project directory already exists.
        NotADirectoryError: If the base_output_dir exists but is not a directory.
        OSError: If there's an OS-related error during directory creation.
    """
    target_project_path = base_output_dir / project_name_original
    logger.info("Target project path: %s", target_project_path)

    try:
        # Check if target exists and has content first
        if target_project_path.exists() and any(target_project_path.iterdir()):
            msg = (
                f"Error: Project directory '{target_project_path}'"
                " already exists and is not empty."
            )
            logger.error(msg)
            raise FileExistsError(msg)

        # Then check base directory
        if not base_output_dir.exists():
            base_output_dir.mkdir(parents=True, exist_ok=True)
        elif not base_output_dir.is_dir():
            click.echo(
                f"Error: Output directory '{base_output_dir}' exists and is a file.",
                err=True,
            )
            raise NotADirectoryError(f"'{base_output_dir}' is a file, not a directory.")

        # Finally create the project directory
        logger.info("Creating project directory: %s", target_project_path)
        target_project_path.mkdir(parents=True)
        return target_project_path
    except Exception as e:
        logger.error("Error creating project directory: %s", e)
        raise


def create_base_structure(
    project_root_path: Path, python_package_slug: str, project_name: str
) -> None:
    """
    Creates the base directory structure and initial files for the project.

    Args:
        project_root_path: The root path of the new project.
        python_package_slug: The slug for the Python package.
        project_name: The original project name for README content.
    Raises:
        OSError: If there's an error creating directories or files.
    """
    logger.info(
        "Creating base project structure in: %s with package slug: %s",
        project_root_path,
        python_package_slug,
    )

    # Create directories
    for dir_template in DEFAULT_PROJECT_STRUCTURE["dirs"]:
        dir_path_str = dir_template.replace(
            "{python_package_slug}", python_package_slug
        )
        dir_path = project_root_path / dir_path_str
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info("Created directory: %s", dir_path)

    # Create files
    for file_template, content_template in DEFAULT_PROJECT_STRUCTURE["files"].items():
        file_path_str = file_template.replace(
            "{python_package_slug}", python_package_slug
        )
        file_path = project_root_path / file_path_str
        file_path.parent.mkdir(parents=True, exist_ok=True)
        # Ensure project_name placeholder is replaced in README content
        content = content_template.replace("{project_name}", project_name)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("Created file: %s", file_path)

    logger.info("Base project structure created successfully at %s", project_root_path)
