"""
Integration tests for project generation functionality.
These tests verify that the directory structure is created correctly.
"""

import shutil
import subprocess
import sys
from pathlib import Path

# Import the helper function directly
PYHATCHERY_CMD = [sys.executable, "-m", "pyhatchery"]


def run_pyhatchery_command(
    args: list[str], cwd: Path | None = None
) -> subprocess.CompletedProcess[str]:
    """Helper function to run pyhatchery CLI commands."""
    command = PYHATCHERY_CMD + args
    return subprocess.run(command, capture_output=True, text=True, check=False, cwd=cwd)


class TestProjectGeneration:
    """Integration tests for project directory structure generation."""

    def test_creates_project_directory_structure(self, tmp_path: Path):
        """Test that the CLI creates the correct project directory structure."""
        # Arrange
        project_name = "TestProject"
        python_package_slug = "testproject"  # Expected derived slug

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
        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )

        # Check that the directory structure was created correctly
        project_root = tmp_path / project_name
        assert project_root.exists(), (
            f"Project root directory not created: {project_root}"
        )
        assert (project_root / "src" / python_package_slug).exists(), (
            f"src/{python_package_slug} directory not created"
        )
        assert (project_root / "tests").exists(), "tests directory not created"
        assert (project_root / "docs").exists(), "docs directory not created"

        # Clean up
        if project_root.exists():
            shutil.rmtree(project_root)

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

        # Clean up
        if project_dir.exists():
            shutil.rmtree(project_dir)
