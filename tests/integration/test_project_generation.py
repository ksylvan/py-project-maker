"""
Integration tests for project generation functionality.
These tests verify that the directory structure is created correctly.
"""

import shutil
from collections.abc import Generator
from pathlib import Path

import pytest
from click.testing import CliRunner

from pyhatchery.cli import cli as pyhatchery_cli
from tests.helpers import (
    get_minimal_non_interactive_args,
    get_sample_project_dir_args,
    run_pyhatchery_command,
)


def _rmdir(path: Path) -> None:
    """Recursively remove a directory."""
    if path.is_dir():
        shutil.rmtree(path)


@pytest.fixture(name="managed_project_base_dir")
def managed_project_base_dir_fixture(tmp_path: Path) -> Generator[Path, None, None]:
    """
    Pytest fixture for managing a base directory for project creation.

    This fixture defines a base directory path within tmp_path.
    It ensures this path is clear before a test and cleans it up afterwards.
    Tests can then create projects inside this base directory.
    """
    base_dir_name = "TestProjectsBase"
    base_dir = tmp_path / base_dir_name

    if base_dir.exists():
        shutil.rmtree(base_dir)
    base_dir.mkdir(parents=True)

    yield base_dir

    shutil.rmtree(base_dir)


@pytest.fixture(name="runner")
def runner_fixture():
    """Fixture that returns a CliRunner instance."""
    return CliRunner()


class TestProjectGeneration:
    """Integration tests for project directory structure generation."""

    def test_creates_project_directory_structure_in_cwd(self, tmp_path: Path):
        """Test CLI creates structure in CWD when no output_dir is given."""
        project_name_to_create = "ProjectInCwd"
        python_package_slug = project_name_to_create.lower()
        project_root_in_tmp = tmp_path / project_name_to_create

        try:
            args = get_minimal_non_interactive_args(project_name_to_create)
            result = run_pyhatchery_command(args, cwd=tmp_path)

            assert result.returncode == 0, (
                f"stdout: {result.stdout}\nstderr: {result.stderr}"
            )
            assert project_root_in_tmp.exists(), (
                f"Project root directory not created: {project_root_in_tmp}"
            )
            assert (project_root_in_tmp / "src" / python_package_slug).exists(), (
                f"src/{python_package_slug} directory not created"
            )
            assert (project_root_in_tmp / "tests").exists(), (
                "tests directory not created"
            )
            assert (project_root_in_tmp / "docs").exists(), "docs directory not created"
        finally:
            _rmdir(project_root_in_tmp)

    def test_creates_project_in_specified_output_directory(
        self, managed_project_base_dir: Path
    ):
        """Test CLI creates project in the directory specified by --output-dir."""
        project_name_to_create = "OutputTestProject"
        python_package_slug = project_name_to_create.lower()
        # The project should be created as a subdirectory of managed_project_base_dir
        expected_project_root = managed_project_base_dir / project_name_to_create

        args = get_minimal_non_interactive_args(project_name_to_create) + [
            "--output-dir",
            str(managed_project_base_dir),
        ]
        # Run from a different CWD to ensure --output-dir is respected
        result = run_pyhatchery_command(args, cwd=Path.cwd())  # Or any other dir

        assert result.returncode == 0, (
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
        assert expected_project_root.exists(), (
            f"Project root directory not created at: {expected_project_root}"
        )
        assert (expected_project_root / "src" / python_package_slug).exists(), (
            f"src/{python_package_slug} directory not created"
        )
        assert (expected_project_root / "tests").exists(), "tests directory not created"
        assert (expected_project_root / "docs").exists(), "docs directory not created"
        # Cleanup is handled by managed_project_base_dir fixture

    def test_fails_if_target_project_path_exists_and_not_empty(
        self, runner: CliRunner, tmp_path: Path
    ):
        """
        Test that project creation fails if the target project directory
        already exists and is not empty.
        """
        project_name = "my_project_nonempty"
        base_output_dir = tmp_path / "custom_output_nonempty"
        base_output_dir.mkdir(parents=True, exist_ok=True)

        project_dir = base_output_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "some_file.txt").write_text("hello")

        # Use direct invoke rather than runner.invoke to avoid potential deadlock
        result = runner.invoke(
            pyhatchery_cli,
            get_sample_project_dir_args(project_name, base_output_dir),
        )

        assert result.exit_code == 1, (
            f"Expected exit code 1, got {result.exit_code}. Stderr: {result.stderr}"
        )
        assert project_dir.exists()
        assert (project_dir / "some_file.txt").exists()

        expected_stderr_part1 = f"Error: Project directory '{project_dir}'"
        expected_stderr_part2 = "already exists and is not empty."

        assert expected_stderr_part1 in result.stderr, (
            f"Expected part1 ('{expected_stderr_part1}') not in stderr. "
            f"Stderr: {result.stderr}"
        )
        assert expected_stderr_part2 in result.stderr, (
            f"Expected part2 ('{expected_stderr_part2}') not in stderr. "
            f"Stderr: {result.stderr}"
        )

    def test_fails_if_output_directory_is_a_file(
        self, runner: CliRunner, tmp_path: Path
    ):
        """
        Test that project creation fails if the specified output directory
        is actually a file.
        """
        project_name = "FileAsOutputDir"
        file_acting_as_output_dir = tmp_path / "iam_a_file.txt"
        file_acting_as_output_dir.write_text("I should not be a directory.")

        _ = runner  # avoid unused variable warning

        try:
            args = get_minimal_non_interactive_args(project_name) + [
                "--output-dir",
                str(file_acting_as_output_dir),
            ]
            result = run_pyhatchery_command(args, cwd=tmp_path)

            assert result.returncode == 2, (
                f"Expected failure with code 2, got {result.returncode}"
            )
            assert (
                "Error: Invalid value for '-o' / '--output-dir': Directory"
                in result.stderr
            )
            assert f"'{str(file_acting_as_output_dir)}'" in result.stderr
            assert "is a file." in result.stderr
        finally:
            if file_acting_as_output_dir.exists():
                file_acting_as_output_dir.unlink()
            _rmdir(tmp_path / project_name)  # Clean up potential project dir
