"""
Integration tests for project generation functionality.
These tests verify that the directory structure is created correctly.
"""

import shutil
import subprocess
import sys
from collections.abc import Generator
from pathlib import Path

import pytest

# Import the helper function directly
PYHATCHERY_CMD = [sys.executable, "-m", "pyhatchery"]


def run_pyhatchery_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Helper function to run pyhatchery CLI commands."""
    command = PYHATCHERY_CMD + args
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=cwd)


def _rmdir(path: Path) -> None:
    """Recursively remove a directory."""
    if path.is_dir():
        shutil.rmtree(path)


@pytest.fixture(name="managed_project_dir")
def managed_project_dir_fixture(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Pytest fixture for project directory management.

    This fixture defines an expected project directory path within tmp_path.
    It ensures this path is clear before a test (if it might exist from a
    previous, failed run) and cleans up the directory after the test.
    The test itself is responsible for the actual creation of this directory
    using the CLI tool.
    """
    project_name = "TestProjectFixture"  # A consistent name for the fixture-managed dir
    project_dir = tmp_path / project_name

    # Pre-test: Ensure the directory is clean if it exists
    if project_dir.exists():
        shutil.rmtree(project_dir)

    yield project_dir  # Provide the path to the test

    # Post-test cleanup: remove the project directory if it was created by the test
    _rmdir(project_dir)


class TestProjectGeneration:
    """Integration tests for project directory structure generation."""

    def test_creates_project_directory_structure(self, managed_project_dir: Path):
        """Test that the CLI creates the correct project directory structure."""
        project_name_to_create = managed_project_dir.name
        python_package_slug = project_name_to_create.lower()

        # Act
        args = [
            "new",
            project_name_to_create,
            "--no-interactive",
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
            "--license",
            "MIT",
            "--python-version",
            "3.11",
        ]
        # Run the command in the parent of managed_project_dir (i.e., tmp_path).
        # The 'new' command is expected to create the 'managed_project_dir' itself.
        result = run_pyhatchery_command(args, cwd=managed_project_dir.parent)

        # Assert
        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Check that the directory structure was created correctly
        # project_root is the path managed and yielded by the fixture
        assert managed_project_dir.exists(), (
            f"Project root directory not created: {managed_project_dir}"
        )
        assert (managed_project_dir / "src" / python_package_slug).exists(), (
            f"src/{python_package_slug} directory not created"
        )
        assert (managed_project_dir / "tests").exists(), "tests directory not created"
        assert (managed_project_dir / "docs").exists(), "docs directory not created"

        # Clean up is handled by the managed_project_dir fixture's teardown phase

    def test_fails_if_project_directory_exists_and_not_empty(self, tmp_path: Path):
        """Test that the CLI fails if the project directory exists and is not empty."""
        # Arrange
        project_name = "ExistingProject"

        # Create a non-empty directory
        project_dir = tmp_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "some_file.txt").write_text("content")

        # Act
        args = [
            "new",
            project_name,
            "--no-interactive",
            "--author",
            "Test Author",
            "--email",
            "test@example.com",
            "--license",
            "MIT",
            "--python-version",
            "3.11",
        ]
        result = run_pyhatchery_command(args, cwd=tmp_path)

        # Assert
        assert result.returncode == 1, f"Expected failure, got: {result.returncode}"
        assert "Error: Project directory" in result.stderr
        assert "already exists and is not empty" in result.stderr

        # Clean up for this specific test case's setup
        _rmdir(project_dir)
