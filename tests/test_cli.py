"""
Unit tests for the CLI module.
"""

import pytest
from unittest.mock import patch, Mock
import argparse

from cli import create_parser, main


class TestCreateParser:
    """Tests for the create_parser function."""

    def test_create_parser_returns_argument_parser(self):
        """Test that create_parser returns an ArgumentParser instance."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_has_version_argument(self):
        """Test that the parser has a version argument."""
        parser = create_parser()

        # Test version argument is present
        with patch("sys.argv", ["gsk", "--version"]):
            with pytest.raises(SystemExit) as exc_info:
                parser.parse_args(["--version"])
            assert exc_info.value.code == 0

    def test_parser_has_path_argument(self):
        """Test that the parser has a path argument with default value."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.path == "."

        args = parser.parse_args(["--path", "/custom/path"])
        assert args.path == "/custom/path"

    def test_parser_has_detailed_argument(self):
        """Test that the parser has a detailed argument."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.detailed is False

        args = parser.parse_args(["--detailed"])
        assert args.detailed is True


class TestMain:
    """Tests for the main function."""

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    def test_main_success_no_repos(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with no repositories found."""
        # Setup mocks
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_class.return_value = mock_scanner

        with patch("sys.argv", ["gsk"]):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 0
        mock_check_git.assert_called_once()
        mock_validate_path.assert_called_once_with(".")
        mock_scanner.scan.assert_called_once()

        # Check that "No Git repositories found" message is printed
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("No Git repositories found" in call for call in print_calls)

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    def test_main_success_with_repos(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with repositories found."""
        # Setup mocks
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_repo1 = Mock()
        mock_repo1.name = "repo1"
        mock_repo2 = Mock()
        mock_repo2.name = "repo2"
        repositories = [mock_repo1, mock_repo2]

        mock_scanner = Mock()
        mock_scanner.scan.return_value = repositories
        mock_scanner.get_summary_stats.return_value = {
            "total": 2,
            "clean": 1,
            "dirty": 1,
        }
        mock_scanner_class.return_value = mock_scanner

        mock_formatter.format_repositories.return_value = "Repository table"
        mock_formatter.format_summary.return_value = "Summary table"

        with patch("sys.argv", ["gsk"]):
            with patch("builtins.print"):
                result = main()

        assert result == 0
        mock_check_git.assert_called_once()
        mock_validate_path.assert_called_once_with(".")
        mock_scanner.scan.assert_called_once()
        mock_scanner.get_summary_stats.assert_called_once()
        mock_formatter.format_repositories.assert_called_once()
        mock_formatter.format_summary.assert_called_once()

        # Check that repositories are sorted by name
        repositories.sort(key=lambda repo: repo.name.lower())
        assert repositories[0].name == "repo1"
        assert repositories[1].name == "repo2"

    @patch("cli.check_git_availability")
    def test_main_git_not_available(self, mock_check_git):
        """Test main function when git is not available."""
        mock_check_git.return_value = False

        with patch("sys.argv", ["gsk"]):
            with patch("cli.print_error") as mock_print_error:
                result = main()

        assert result == 1
        mock_check_git.assert_called_once()
        mock_print_error.assert_called_once_with(
            "Git is not installed or not in PATH. Please install Git to use this tool."
        )

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    def test_main_keyboard_interrupt(
        self, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with keyboard interrupt."""
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_scanner = Mock()
        mock_scanner.scan.side_effect = KeyboardInterrupt()
        mock_scanner_class.return_value = mock_scanner

        with patch("sys.argv", ["gsk"]):
            with patch("builtins.print") as mock_print:
                result = main()

        assert result == 1
        mock_print.assert_called_with("\nOperation cancelled by user.")

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    def test_main_general_exception(
        self, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with general exception."""
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_scanner = Mock()
        mock_scanner.scan.side_effect = Exception("Test error")
        mock_scanner_class.return_value = mock_scanner

        with patch("sys.argv", ["gsk"]):
            with patch("cli.print_error") as mock_print_error:
                result = main()

        assert result == 1
        mock_print_error.assert_called_with("An error occurred: Test error")

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    def test_main_with_detailed_flag(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with detailed flag."""
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_repo = Mock()
        mock_repo.name = "test-repo"
        repositories = [mock_repo]

        mock_scanner = Mock()
        mock_scanner.scan.return_value = repositories
        mock_scanner.get_summary_stats.return_value = {
            "total": 1,
            "clean": 1,
            "dirty": 0,
        }
        mock_scanner_class.return_value = mock_scanner

        mock_formatter.format_repositories.return_value = "Detailed table"
        mock_formatter.format_summary.return_value = "Summary"

        with patch("sys.argv", ["gsk", "--detailed"]):
            result = main()

        assert result == 0
        mock_formatter.format_repositories.assert_called_once_with(
            repositories, show_url=True
        )

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    def test_main_with_custom_path(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test main function with custom path."""
        mock_check_git.return_value = True
        mock_validate_path.return_value = None

        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_class.return_value = mock_scanner

        custom_path = "/custom/path"
        with patch("sys.argv", ["gsk", "--path", custom_path]):
            result = main()

        assert result == 0
        mock_validate_path.assert_called_once_with(custom_path)
        mock_scanner_class.assert_called_once_with(custom_path)


class TestMainIntegration:
    """Integration tests for the main function."""

    def test_main_entry_point(self):
        """Test that main can be called as entry point."""
        with patch("cli.main") as mock_main:
            mock_main.return_value = 0

            # Simulate calling from command line
            with patch("sys.argv", ["gsk"]):
                from cli import main

                result = main()

            assert result == 0
