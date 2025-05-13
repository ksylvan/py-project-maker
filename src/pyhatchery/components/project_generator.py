"""Project generator component for PyHatchery.

This module handles the creation of the basic directory structure for new projects.
"""

from pathlib import Path


def create_base_structure(
    output_path: Path, project_name_original: str, python_package_slug: str
) -> Path:
    """Create the basic directory structure for a new project.

    Args:
        output_path: The base output path where the project will be created.
        project_name_original: The original project name as provided by the user.
        python_package_slug: The Python package slug (e.g., "my_project").

    Returns:
        The path to the created project root directory.

    Raises:
        FileExistsError: If the project directory already exists and is not empty.
        OSError: If there's an error creating the directories.
    """
    # Create the root project directory
    project_root = output_path / project_name_original

    # Check if the directory already exists and is not empty
    if project_root.exists() and any(project_root.iterdir()):
        raise FileExistsError(
            f"Project directory '{project_root}' already exists and is not empty."
        )

    # Create the root directory
    project_root.mkdir(parents=True, exist_ok=True)

    # Create the src/package_name directory
    src_package_dir = project_root / "src" / python_package_slug
    src_package_dir.mkdir(parents=True, exist_ok=True)

    # Create the tests directory
    tests_dir = project_root / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    # Create the docs directory
    docs_dir = project_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    return project_root
