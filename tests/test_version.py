"""
Unit tests for the version utility functions.
"""

import pytest
from unittest.mock import patch
from importlib.metadata import PackageNotFoundError

from utils import get_current_version


class TestGetCurrentVersion:
    """Tests for get_current_version function."""

    @patch("utils.version.version")
    def test_get_current_version_success(self, mock_version):
        """Test get_current_version when package is found."""
        mock_version.return_value = "1.2.3"

        result = get_current_version()

        assert result == "1.2.3"
        mock_version.assert_called_once_with("gitskan")

    @patch("utils.version.version")
    def test_get_current_version_package_not_found(self, mock_version):
        """Test get_current_version when package is not found."""
        mock_version.side_effect = PackageNotFoundError()

        result = get_current_version()

        assert result == "unknown"
        mock_version.assert_called_once_with("gitskan")

    @patch("utils.version.version")
    def test_get_current_version_dev_version(self, mock_version):
        """Test get_current_version with development version."""
        mock_version.return_value = "1.0.0.dev0"

        result = get_current_version()

        assert result == "1.0.0.dev0"

    @patch("utils.version.version")
    def test_get_current_version_pre_release(self, mock_version):
        """Test get_current_version with pre-release version."""
        mock_version.return_value = "2.0.0a1"

        result = get_current_version()

        assert result == "2.0.0a1"

    @patch("utils.version.version")
    def test_get_current_version_rc_version(self, mock_version):
        """Test get_current_version with release candidate version."""
        mock_version.return_value = "1.5.0rc2"

        result = get_current_version()

        assert result == "1.5.0rc2"

    @patch("utils.version.version")
    def test_get_current_version_post_release(self, mock_version):
        """Test get_current_version with post-release version."""
        mock_version.return_value = "1.0.0.post1"

        result = get_current_version()

        assert result == "1.0.0.post1"

    @patch("utils.version.version")
    def test_get_current_version_empty_string(self, mock_version):
        """Test get_current_version with empty string version."""
        mock_version.return_value = ""

        result = get_current_version()

        assert result == ""

    @patch("utils.version.version")
    def test_get_current_version_none(self, mock_version):
        """Test get_current_version with None version."""
        mock_version.return_value = None

        result = get_current_version()

        assert result is None

    @patch("utils.version.version")
    def test_get_current_version_very_long_version(self, mock_version):
        """Test get_current_version with very long version string."""
        long_version = "1.0.0+build.1.2.3.4.5.6.7.8.9.10.very.long.build.identifier"
        mock_version.return_value = long_version

        result = get_current_version()

        assert result == long_version

    @patch("utils.version.version")
    def test_get_current_version_semantic_version(self, mock_version):
        """Test get_current_version with semantic version."""
        mock_version.return_value = "1.0.0+20130313144700"

        result = get_current_version()

        assert result == "1.0.0+20130313144700"

    @patch("utils.version.version")
    def test_get_current_version_calls_correct_package(self, mock_version):
        """Test that get_current_version calls version with correct package name."""
        mock_version.return_value = "1.0.0"

        get_current_version()

        mock_version.assert_called_once_with("gitskan")

    @patch("utils.version.version")
    def test_get_current_version_exception_handling(self, mock_version):
        """Test that get_current_version handles exceptions gracefully."""
        # Test with different exception types that might occur
        mock_version.side_effect = PackageNotFoundError("Package 'gitskan' not found")

        result = get_current_version()

        assert result == "unknown"

        # Test with a different exception (should not be caught)
        mock_version.side_effect = ValueError("Invalid package name")

        with pytest.raises(ValueError):
            get_current_version()


class TestVersionIntegration:
    """Integration tests for version functions."""

    def test_get_current_version_return_type(self):
        """Test that get_current_version returns a string."""
        with patch("utils.version.version") as mock_version:
            mock_version.return_value = "1.0.0"

            result = get_current_version()

            assert isinstance(result, str)

    def test_get_current_version_unknown_return_type(self):
        """Test that get_current_version returns string when package not found."""
        with patch("utils.version.version") as mock_version:
            mock_version.side_effect = PackageNotFoundError()

            result = get_current_version()

            assert isinstance(result, str)
            assert result == "unknown"

    def test_get_current_version_consistency(self):
        """Test that get_current_version returns consistent results."""
        with patch("utils.version.version") as mock_version:
            mock_version.return_value = "1.2.3"

            result1 = get_current_version()
            result2 = get_current_version()

            assert result1 == result2
            assert result1 == "1.2.3"
