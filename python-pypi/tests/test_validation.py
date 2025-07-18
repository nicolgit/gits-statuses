"""
Unit tests for the validation utility functions.
"""

import pytest
from unittest.mock import patch, Mock
import subprocess
import sys
from pathlib import Path

from utils import check_git_availability, validate_path


class TestCheckGitAvailability:
    """Tests for check_git_availability function."""

    @patch("subprocess.run")
    def test_check_git_availability_success(self, mock_run):
        """Test check_git_availability when git is available."""
        mock_run.return_value = Mock()

        result = check_git_availability()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "--version"], capture_output=True, check=True
        )

    @patch("subprocess.run")
    def test_check_git_availability_subprocess_error(self, mock_run):
        """Test check_git_availability with subprocess error."""
        mock_run.side_effect = subprocess.SubprocessError()

        result = check_git_availability()

        assert result is False

    @patch("subprocess.run")
    def test_check_git_availability_file_not_found(self, mock_run):
        """Test check_git_availability when git is not found."""
        mock_run.side_effect = FileNotFoundError()

        result = check_git_availability()

        assert result is False

    @patch("subprocess.run")
    def test_check_git_availability_called_process_error(self, mock_run):
        """Test check_git_availability with CalledProcessError."""
        mock_run.side_effect = subprocess.CalledProcessError(1, ["git", "--version"])

        result = check_git_availability()

        assert result is False


class TestValidatePath:
    """Tests for validate_path function."""

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_validate_path_success(self, mock_is_dir, mock_exists):
        """Test validate_path with valid directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = validate_path("/valid/path")

        assert isinstance(result, Path)
        assert str(result) == "/valid/path"
        mock_exists.assert_called_once()
        mock_is_dir.assert_called_once()

    @patch("pathlib.Path.exists")
    @patch("builtins.print")
    def test_validate_path_does_not_exist(self, mock_print, mock_exists):
        """Test validate_path with non-existent path."""
        mock_exists.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            validate_path("/non/existent/path")

        assert exc_info.value.code == 1
        mock_print.assert_called_once_with(
            "Error: Path '/non/existent/path' does not exist.", file=sys.stderr
        )

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    @patch("builtins.print")
    def test_validate_path_not_directory(self, mock_print, mock_is_dir, mock_exists):
        """Test validate_path with file instead of directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = False

        with pytest.raises(SystemExit) as exc_info:
            validate_path("/path/to/file.txt")

        assert exc_info.value.code == 1
        mock_print.assert_called_once_with(
            "Error: Path '/path/to/file.txt' is not a directory.", file=sys.stderr
        )

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_validate_path_relative_path(self, mock_is_dir, mock_exists):
        """Test validate_path with relative path."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = validate_path("./relative/path")

        assert isinstance(result, Path)
        assert str(result) == "relative/path"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_validate_path_current_directory(self, mock_is_dir, mock_exists):
        """Test validate_path with current directory."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = validate_path(".")

        assert isinstance(result, Path)
        assert str(result) == "."

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_validate_path_empty_string(self, mock_is_dir, mock_exists):
        """Test validate_path with empty string."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = validate_path("")

        assert isinstance(result, Path)
        assert str(result) == "."  # Empty string becomes current directory

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.is_dir")
    def test_validate_path_with_spaces(self, mock_is_dir, mock_exists):
        """Test validate_path with path containing spaces."""
        mock_exists.return_value = True
        mock_is_dir.return_value = True

        result = validate_path("/path with spaces/directory")

        assert isinstance(result, Path)
        assert str(result) == "/path with spaces/directory"


class TestValidationIntegration:
    """Integration tests for validation functions."""

    def test_check_git_availability_real_call(self):
        """Test check_git_availability with real subprocess call."""
        # This test depends on git being available in the test environment
        # We'll mock it to avoid dependency on actual git installation
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock()
            result = check_git_availability()
            assert result is True

    def test_validate_path_with_real_path(self):
        """Test validate_path with real filesystem path."""
        # Use a path that should exist in most environments
        with patch("pathlib.Path.exists", return_value=True), patch(
            "pathlib.Path.is_dir", return_value=True
        ):
            result = validate_path("/tmp")
            assert isinstance(result, Path)
            assert str(result) == "/tmp"
