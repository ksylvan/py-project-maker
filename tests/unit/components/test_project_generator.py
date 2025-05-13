"""Unit tests for the project generator component."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pyhatchery.components.project_generator import create_base_structure


class TestCreateBaseStructure:
    """Tests for the create_base_structure function."""

    def test_creates_correct_directory_structure(self, tmp_path: Path):
        """Test that the function creates the correct directory structure."""
        # Arrange
        output_path = tmp_path
        project_name = "Test Project"
        python_package_slug = "test_project"

        # Act
        project_root = create_base_structure(
            output_path, project_name, python_package_slug
        )

        # Assert
        assert project_root == output_path / project_name
        assert (output_path / project_name).exists()
        assert (output_path / project_name / "src" / python_package_slug).exists()
        assert (output_path / project_name / "tests").exists()
        assert (output_path / project_name / "docs").exists()

    def test_raises_error_if_directory_exists_and_not_empty(self, tmp_path: Path):
        """Test error when directory exists and is not empty."""
        # Arrange
        output_path = tmp_path
        project_name = "Test Project"
        python_package_slug = "test_project"

        # Create the directory and add a file to make it non-empty
        project_dir = output_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        (project_dir / "some_file.txt").write_text("content")

        # Act & Assert
        with pytest.raises(FileExistsError):
            create_base_structure(output_path, project_name, python_package_slug)

    def test_handles_empty_existing_directory(self, tmp_path: Path):
        """Test that the function handles an empty existing directory."""
        # Arrange
        output_path = tmp_path
        project_name = "Test Project"
        python_package_slug = "test_project"

        # Create an empty directory
        project_dir = output_path / project_name
        project_dir.mkdir(parents=True, exist_ok=True)

        # Act
        project_root = create_base_structure(
            output_path, project_name, python_package_slug
        )

        # Assert
        assert project_root == output_path / project_name
        assert (output_path / project_name / "src" / python_package_slug).exists()
        assert (output_path / project_name / "tests").exists()
        assert (output_path / project_name / "docs").exists()

    @patch("pathlib.Path.mkdir")
    def test_handles_os_error(self, mock_mkdir: MagicMock, tmp_path: Path):
        """Test that the function handles OSError correctly."""
        # Arrange
        output_path = tmp_path
        project_name = "Test Project"
        python_package_slug = "test_project"

        # Make mkdir raise an OSError
        mock_mkdir.side_effect = OSError("Permission denied")

        # Act & Assert
        with pytest.raises(OSError):
            create_base_structure(output_path, project_name, python_package_slug)
