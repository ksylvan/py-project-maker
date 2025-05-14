"""Unit tests for the project generator component."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyhatchery.components.project_generator import (
    create_base_structure,
    setup_project_directory,
)


class TestSetupProjectDirectory:
    """Tests for the setup_project_directory function."""

    def test_creates_target_project_dir_and_base_if_not_exists(self, tmp_path: Path):
        """Test creation when base_output_dir and target_project_path don't exist."""
        base_output_dir = tmp_path / "custom_output"
        project_name = "TestProject"
        expected_project_path = base_output_dir / project_name

        returned_path = setup_project_directory(base_output_dir, project_name)

        assert returned_path == expected_project_path
        assert base_output_dir.exists()
        assert base_output_dir.is_dir()
        assert expected_project_path.exists()
        assert expected_project_path.is_dir()

    def test_creates_target_project_dir_if_base_exists(self, tmp_path: Path):
        """Test creation when base_output_dir exists but target does not."""
        base_output_dir = tmp_path
        project_name = "TestProject"
        expected_project_path = base_output_dir / project_name

        base_output_dir.mkdir(parents=True, exist_ok=True)

        returned_path = setup_project_directory(base_output_dir, project_name)

        assert returned_path == expected_project_path
        assert expected_project_path.exists()
        assert expected_project_path.is_dir()

    def test_raises_file_exists_error_if_target_project_path_exists(
        self, tmp_path: Path
    ):
        """Test FileExistsError if target_project_path already exists."""
        base_output_dir = tmp_path
        project_name = "ExistingProject"
        target_project_path = base_output_dir / project_name
        target_project_path.mkdir(parents=True, exist_ok=True)

        with pytest.raises(FileExistsError) as exception_info:
            setup_project_directory(base_output_dir, project_name)
        assert str(target_project_path) in str(exception_info.value)

    def test_raises_not_a_directory_error_if_base_output_is_file(self, tmp_path: Path):
        """Test NotADirectoryError if base_output_dir is a file."""
        base_output_dir_as_file = tmp_path / "file.txt"
        base_output_dir_as_file.write_text("I am a file.")
        project_name = "TestProject"

        with pytest.raises(NotADirectoryError) as exception_info:
            setup_project_directory(base_output_dir_as_file, project_name)
        assert str(base_output_dir_as_file) in str(exception_info.value)

    @patch("pathlib.Path.mkdir")
    def test_raises_os_error_on_base_dir_creation_failure(
        self, mock_mkdir: MagicMock, tmp_path: Path
    ):
        """Test OSError if base_output_dir.mkdir() fails."""
        base_output_dir = tmp_path / "custom_output"  # This dir does not exist
        project_name = "TestProject"

        # setup_project_directory will call:
        # 1. base_output_dir.mkdir(parents=True, exist_ok=True) -> fail this
        mock_mkdir.side_effect = OSError("Permission denied for base")

        with pytest.raises(OSError, match="Permission denied for base"):
            setup_project_directory(base_output_dir, project_name)

        # Assert that the failing call was for base_output_dir
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch("pathlib.Path.mkdir")
    def test_raises_os_error_on_target_dir_creation_failure(
        self, mock_mkdir: MagicMock, tmp_path: Path
    ):
        """Test OSError if target_project_path.mkdir() fails."""
        base_output_dir = tmp_path
        project_name = "TestProjectTargetFail"

        # Ensure base_output_dir exists (use original mkdir, not the mock)
        # This is to ensure the SUT's first mkdir call is for the target.
        with patch("pathlib.Path.mkdir", new=Path.mkdir):  # Use original mkdir
            base_output_dir.mkdir(parents=True, exist_ok=True)

        # Reset mock_mkdir to forget calls during fixture setup or explicit creation.
        mock_mkdir.reset_mock()

        # setup_project_directory, when base_output_dir exists, will call:
        # 1. (base_output_dir / project_name).mkdir(parents=True) -> fail this
        mock_mkdir.side_effect = OSError("Permission denied for target")

        with pytest.raises(OSError, match="Permission denied for target"):
            setup_project_directory(base_output_dir, project_name)

        # Assert that mkdir was called for the target project path
        mock_mkdir.assert_called_once_with(parents=True)


class TestCreateBaseStructure:
    """Tests for the create_base_structure function."""

    def test_creates_correct_directory_structure(self, tmp_path: Path):
        """Test that the function creates the correct directory structure."""
        project_root_path = tmp_path / "TestProject"
        project_root_path.mkdir(parents=True, exist_ok=True)

        project_name_for_readme = "Test Project Display Name"
        python_package_slug = "test_project_slug"

        create_base_structure(
            project_root_path, python_package_slug, project_name_for_readme
        )

        assert (project_root_path / "src" / python_package_slug).exists()
        assert (
            project_root_path / "src" / python_package_slug / "__init__.py"
        ).exists()
        assert (project_root_path / "tests").exists()
        assert (project_root_path / "tests" / "__init__.py").exists()
        assert (project_root_path / "docs").exists()
        assert (project_root_path / "README.md").exists()
        assert (project_root_path / ".gitignore").exists()

        readme_content = (project_root_path / "README.md").read_text()
        assert f"# {project_name_for_readme}" in readme_content

    def test_works_with_empty_existing_project_root_directory(self, tmp_path: Path):
        """Test function with an empty existing project_root_path."""
        project_root_path = tmp_path / "EmptyExistingProject"
        project_root_path.mkdir(parents=True, exist_ok=True)

        project_name_for_readme = "Empty Existing Project"
        python_package_slug = "empty_existing_project"

        create_base_structure(
            project_root_path, python_package_slug, project_name_for_readme
        )

        assert (project_root_path / "src" / python_package_slug).exists()
        assert (project_root_path / "tests").exists()
        assert (project_root_path / "docs").exists()
        readme_content = (project_root_path / "README.md").read_text()
        assert f"# {project_name_for_readme}" in readme_content

    @patch("pathlib.Path.mkdir")
    def test_handles_os_error_during_subdir_creation(
        self, mock_mkdir: MagicMock, tmp_path: Path
    ):
        """Test OSError during subdirectory creation."""
        project_root_path = tmp_path / "OSErrorProjectSubdir"
        # Create project_root_path directly, not via the mock
        # Use original mkdir for setup
        with patch("pathlib.Path.mkdir", new=Path.mkdir):
            project_root_path.mkdir(parents=True, exist_ok=True)

        project_name_for_readme = "OS Error Subdir Project"
        python_package_slug = "os_error_subdir_project"

        mock_mkdir.side_effect = OSError("Permission denied for subdir")

        with pytest.raises(OSError, match="Permission denied for subdir"):
            create_base_structure(
                project_root_path, python_package_slug, project_name_for_readme
            )

        # create_base_structure calls dir_path.mkdir(parents=True, exist_ok=True)
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)

    @patch("builtins.open", new_callable=MagicMock)
    def test_handles_os_error_during_file_creation(
        self, mock_open: MagicMock, tmp_path: Path
    ):
        """Test OSError during file creation."""
        project_root_path = tmp_path / "FileErrorProject"
        project_root_path.mkdir(parents=True, exist_ok=True)

        project_name_for_readme = "File Error Project"
        python_package_slug = "file_error_project"

        mock_open.side_effect = OSError("Cannot write file")

        with pytest.raises(OSError, match="Cannot write file"):
            create_base_structure(
                project_root_path, python_package_slug, project_name_for_readme
            )

        # Assert open was called for the first file create_base_structure tries.
        # This is typically src/{python_package_slug}/__init__.py.
        expected_init_path = (
            project_root_path / "src" / python_package_slug / "__init__.py"
        )
        mock_open.assert_any_call(expected_init_path, "w", encoding="utf-8")
