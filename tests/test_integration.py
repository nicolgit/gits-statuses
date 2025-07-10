"""
Integration tests for the gitskan application.
"""

from unittest.mock import patch, Mock
from pathlib import Path


from cli import main
from src.git_tools import GitRepository, TableFormatter


class TestCliIntegration:
    """Integration tests for the CLI application."""

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    @patch("sys.argv", ["gsk"])
    def test_cli_full_workflow_no_repositories(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test full CLI workflow with no repositories found."""
        # Setup mocks
        mock_check_git.return_value = True
        mock_validate_path.return_value = Path(".")

        mock_scanner = Mock()
        mock_scanner.scan.return_value = []
        mock_scanner_class.return_value = mock_scanner

        with patch("builtins.print") as mock_print:
            result = main()

        assert result == 0
        mock_check_git.assert_called_once()
        mock_validate_path.assert_called_once_with(".")
        mock_scanner.scan.assert_called_once()

        # Verify output
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("No Git repositories found" in call for call in print_calls)

    @patch("cli.check_git_availability")
    @patch("cli.validate_path")
    @patch("cli.GitScanner")
    @patch("cli.TableFormatter")
    @patch("sys.argv", ["gsk", "--detailed"])
    def test_cli_full_workflow_with_repositories(
        self, mock_formatter, mock_scanner_class, mock_validate_path, mock_check_git
    ):
        """Test full CLI workflow with repositories found."""
        # Setup mocks
        mock_check_git.return_value = True
        mock_validate_path.return_value = Path(".")

        # Create mock repositories
        mock_repo1 = Mock()
        mock_repo1.name = "repo1"
        mock_repo2 = Mock()
        mock_repo2.name = "repo2"
        repositories = [mock_repo1, mock_repo2]

        mock_scanner = Mock()
        mock_scanner.scan.return_value = repositories
        mock_scanner.get_summary_stats.return_value = {
            "total_repos": 2,
            "repos_with_changes": 1,
            "repos_ahead": 0,
            "repos_behind": 1,
            "repos_with_untracked": 1,
        }
        mock_scanner_class.return_value = mock_scanner

        mock_formatter.format_repositories.return_value = "Repository Table"
        mock_formatter.format_summary.return_value = "Summary Table"

        with patch("builtins.print"):
            result = main()

        assert result == 0
        mock_formatter.format_repositories.assert_called_once_with(
            repositories, show_url=True
        )
        mock_formatter.format_summary.assert_called_once()
        mock_scanner.get_summary_stats.assert_called_once()

    @patch("cli.check_git_availability")
    @patch("sys.argv", ["gsk"])
    def test_cli_git_not_available(self, mock_check_git):
        """Test CLI when git is not available."""
        mock_check_git.return_value = False

        with patch("cli.print_error") as mock_print_error:
            result = main()

        assert result == 1
        mock_print_error.assert_called_once_with(
            "Git is not installed or not in PATH. Please install Git to use this tool."
        )


class TestScannerRepositoryIntegration:
    """Integration tests for GitScanner and GitRepository."""

    @patch("subprocess.run")
    def test_repository_git_operations_integration(self, mock_run):
        """Test GitRepository integration with git operations."""
        # Mock git command responses
        mock_run.side_effect = [
            # _is_git_repository
            Mock(returncode=0, stdout="true"),
            # _get_current_branch
            Mock(returncode=0, stdout="main\n"),
            # _get_remote_url
            Mock(returncode=0, stdout="https://github.com/user/repo.git\n"),
            # _get_ahead_count - upstream check
            Mock(returncode=0, stdout="origin/main\n"),
            # _get_ahead_count - count
            Mock(returncode=0, stdout="2\n"),
            # _get_behind_count - upstream check
            Mock(returncode=0, stdout="origin/main\n"),
            # _get_behind_count - count
            Mock(returncode=0, stdout="1\n"),
            # _get_changed_count
            Mock(returncode=0, stdout=" M file1.txt\n?? file2.txt\n"),
            # _get_untracked_count
            Mock(returncode=0, stdout=" M file1.txt\n?? file2.txt\n"),
            # _get_total_commits
            Mock(returncode=0, stdout="42\n"),
        ]

        repo = GitRepository("/path/to/repo")

        assert repo.is_valid is True
        assert repo.branch == "main"
        assert repo.remote_url == "https://github.com/user/repo.git"
        assert repo.ahead_count == 2
        assert repo.behind_count == 1
        assert repo.changed_count == 2
        assert repo.untracked_count == 1
        assert repo.total_commits == 42
        assert repo.status == "↑2 ↓1 ~2 ?1"
        assert repo.has_changes() is True


class TestFormatterIntegration:
    """Integration tests for TableFormatter with repository data."""

    def test_formatter_summary_integration(self):
        """Test TableFormatter summary with scanner statistics."""
        # Create mock scanner with realistic stats
        scanner = Mock()
        scanner.get_summary_stats.return_value = {
            "total_repos": 10,
            "repos_with_changes": 3,
            "repos_ahead": 2,
            "repos_behind": 1,
            "repos_with_untracked": 4,
        }

        stats = scanner.get_summary_stats()
        summary = TableFormatter.format_summary(stats)

        assert "Total repositories: 10" in summary
        assert "Repositories with changes: 3" in summary
        assert "Repositories ahead of remote: 2" in summary
        assert "Repositories behind remote: 1" in summary
        assert "Repositories with untracked files: 4" in summary
