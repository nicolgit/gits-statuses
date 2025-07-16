"""
Unit tests for the GitScanner class.
"""

from unittest.mock import patch, Mock
from pathlib import Path

from git_tools import GitScanner


class TestGitScannerInit:
    """Tests for GitScanner initialization."""

    def test_init_default_path(self):
        """Test initialization with default path."""
        scanner = GitScanner()
        assert isinstance(scanner.scan_path, Path)
        assert scanner.scan_path.is_absolute()
        assert scanner.repositories == []

    def test_init_custom_path(self):
        """Test initialization with custom path."""
        custom_path = "/custom/path"
        scanner = GitScanner(custom_path)
        assert scanner.scan_path == Path(custom_path).resolve()
        assert scanner.repositories == []


class TestGitScannerDirectoryCheck:
    """Tests for directory git repository checking."""

    def test_is_directory_git_repo_true(self):
        """Test _is_directory_git_repo with git repository."""
        scanner = GitScanner()
        test_path = Path("/path/to/repo")

        with patch.object(Path, "exists", return_value=True):
            result = scanner._is_directory_git_repo(test_path)

        assert result is True

    def test_is_directory_git_repo_false(self):
        """Test _is_directory_git_repo with non-git directory."""
        scanner = GitScanner()
        test_path = Path("/path/to/non-repo")

        with patch.object(Path, "exists", return_value=False):
            result = scanner._is_directory_git_repo(test_path)

        assert result is False


class TestGitScannerScan:
    """Tests for the scan method."""

    @patch("git_tools.scanner.GitRepository")
    @patch("builtins.print")
    def test_scan_current_directory_is_repo(self, mock_print, mock_git_repo):
        """Test scan when current directory is a git repository."""
        # Mock the repository
        mock_repo = Mock()
        mock_repo.is_valid = True
        mock_git_repo.return_value = mock_repo

        # Mock the Path constructor to return a mock path that we can control
        with patch("git_tools.scanner.Path") as mock_path_class:
            mock_path_instance = Mock()
            mock_path_instance.resolve.return_value = mock_path_instance
            mock_path_instance.iterdir.return_value = []
            mock_path_class.return_value = mock_path_instance

            scanner = GitScanner("/path/to/repo")

            with patch.object(scanner, "_is_directory_git_repo", return_value=True):
                result = scanner.scan()

        assert len(result) == 1
        assert result[0] == mock_repo
        assert mock_repo in scanner.repositories
        mock_print.assert_called_once_with(
            f"Scanning for Git repositories in: {scanner.scan_path}"
        )

    @patch("git_tools.scanner.GitRepository")
    @patch("builtins.print")
    def test_scan_subdirectories(self, mock_print, mock_git_repo):
        """Test scan with subdirectories containing git repositories."""
        # Mock subdirectories
        mock_dir1 = Mock()
        mock_dir1.is_dir.return_value = True
        mock_dir1.name = "repo1"

        mock_dir2 = Mock()
        mock_dir2.is_dir.return_value = True
        mock_dir2.name = "repo2"

        mock_file = Mock()
        mock_file.is_dir.return_value = False
        mock_file.name = "file.txt"

        mock_hidden_dir = Mock()
        mock_hidden_dir.is_dir.return_value = True
        mock_hidden_dir.name = ".hidden"

        # Mock repositories
        mock_repo1 = Mock()
        mock_repo1.is_valid = True
        mock_repo2 = Mock()
        mock_repo2.is_valid = True

        mock_git_repo.side_effect = [mock_repo1, mock_repo2]

        # Mock the Path constructor to return a mock path that we can control
        with patch("git_tools.scanner.Path") as mock_path_class:
            mock_path_instance = Mock()
            mock_path_instance.resolve.return_value = mock_path_instance
            mock_path_instance.iterdir.return_value = [
                mock_dir1,
                mock_dir2,
                mock_file,
                mock_hidden_dir,
            ]
            mock_path_class.return_value = mock_path_instance

            scanner = GitScanner("/path/to/scan")

            with patch.object(scanner, "_is_directory_git_repo") as mock_is_git_repo:
                # Current directory is not a git repo
                mock_is_git_repo.side_effect = [False, True, True]

                result = scanner.scan()

        assert len(result) == 2
        assert mock_repo1 in result
        assert mock_repo2 in result

        # Verify that hidden directories and files are skipped
        assert (
            mock_is_git_repo.call_count == 3
        )  # current dir + 2 subdirs (hidden dir and file are skipped)

    @patch("git_tools.scanner.GitRepository")
    @patch("builtins.print")
    def test_scan_invalid_repositories_filtered(self, mock_print, mock_git_repo):
        """Test scan filters out invalid repositories."""
        # Mock subdirectory
        mock_dir = Mock()
        mock_dir.is_dir.return_value = True
        mock_dir.name = "invalid-repo"

        # Mock invalid repository
        mock_repo = Mock()
        mock_repo.is_valid = False
        mock_git_repo.return_value = mock_repo

        # Mock the Path constructor to return a mock path that we can control
        with patch("git_tools.scanner.Path") as mock_path_class:
            mock_path_instance = Mock()
            mock_path_instance.resolve.return_value = mock_path_instance
            mock_path_instance.iterdir.return_value = [mock_dir]
            mock_path_class.return_value = mock_path_instance

            scanner = GitScanner("/path/to/scan")

            with patch.object(scanner, "_is_directory_git_repo", return_value=True):
                result = scanner.scan()

        assert len(result) == 0
        assert len(scanner.repositories) == 0

    @patch("builtins.print")
    def test_scan_permission_error(self, mock_print):
        """Test scan handles permission errors gracefully."""
        # Mock the Path constructor to return a mock path that we can control
        with patch("git_tools.scanner.Path") as mock_path_class:
            mock_path_instance = Mock()
            mock_path_instance.resolve.return_value = mock_path_instance
            mock_path_instance.iterdir.side_effect = PermissionError()
            mock_path_class.return_value = mock_path_instance

            scanner = GitScanner("/path/to/restricted")

            with patch.object(scanner, "_is_directory_git_repo", return_value=False):
                result = scanner.scan()

        assert len(result) == 0
        mock_print.assert_any_call(f"Permission denied accessing: {scanner.scan_path}")

    @patch("git_tools.scanner.GitRepository")
    @patch("builtins.print")
    def test_scan_empty_directory(self, mock_print, mock_git_repo):
        """Test scan with empty directory."""
        # Mock the Path constructor to return a mock path that we can control
        with patch("git_tools.scanner.Path") as mock_path_class:
            mock_path_instance = Mock()
            mock_path_instance.resolve.return_value = mock_path_instance
            mock_path_instance.iterdir.return_value = []
            mock_path_class.return_value = mock_path_instance

            scanner = GitScanner("/path/to/empty")

            with patch.object(scanner, "_is_directory_git_repo", return_value=False):
                result = scanner.scan()

        assert len(result) == 0
        assert len(scanner.repositories) == 0


class TestGitScannerRepositoryFiltering:
    """Tests for repository filtering methods."""

    def test_get_repositories_with_changes(self):
        """Test get_repositories_with_changes method."""
        scanner = GitScanner()

        # Create mock repositories
        clean_repo = Mock()
        clean_repo.has_changes.return_value = False

        dirty_repo = Mock()
        dirty_repo.has_changes.return_value = True

        another_dirty_repo = Mock()
        another_dirty_repo.has_changes.return_value = True

        scanner.repositories = [clean_repo, dirty_repo, another_dirty_repo]

        result = scanner.get_repositories_with_changes()

        assert len(result) == 2
        assert dirty_repo in result
        assert another_dirty_repo in result
        assert clean_repo not in result

    def test_get_repositories_with_changes_empty(self):
        """Test get_repositories_with_changes with no repositories."""
        scanner = GitScanner()
        scanner.repositories = []

        result = scanner.get_repositories_with_changes()

        assert result == []


class TestGitScannerSummaryStats:
    """Tests for summary statistics generation."""

    def test_get_summary_stats_mixed_repositories(self):
        """Test get_summary_stats with mixed repository states."""
        scanner = GitScanner()

        # Create mock repositories with different states
        clean_repo = Mock()
        clean_repo.changed_count = 0
        clean_repo.ahead_count = 0
        clean_repo.behind_count = 0
        clean_repo.untracked_count = 0

        dirty_repo = Mock()
        dirty_repo.changed_count = 3
        dirty_repo.ahead_count = 2
        dirty_repo.behind_count = 0
        dirty_repo.untracked_count = 1

        behind_repo = Mock()
        behind_repo.changed_count = 0
        behind_repo.ahead_count = 0
        behind_repo.behind_count = 1
        behind_repo.untracked_count = 0

        untracked_repo = Mock()
        untracked_repo.changed_count = 0
        untracked_repo.ahead_count = 0
        untracked_repo.behind_count = 0
        untracked_repo.untracked_count = 2

        scanner.repositories = [clean_repo, dirty_repo, behind_repo, untracked_repo]

        result = scanner.get_summary_stats()

        assert (
            result
            == {
                "total_repos": 4,
                "repos_with_changes": 1,  # Only dirty_repo has changed_count > 0
                "repos_ahead": 1,  # Only dirty_repo has ahead_count > 0
                "repos_behind": 1,  # Only behind_repo has behind_count > 0
                "repos_with_untracked": 2,  # dirty_repo and untracked_repo have untracked_count > 0
            }
        )

    def test_get_summary_stats_empty(self):
        """Test get_summary_stats with no repositories."""
        scanner = GitScanner()
        scanner.repositories = []

        result = scanner.get_summary_stats()

        assert result == {
            "total_repos": 0,
            "repos_with_changes": 0,
            "repos_ahead": 0,
            "repos_behind": 0,
            "repos_with_untracked": 0,
        }

    def test_get_summary_stats_all_clean(self):
        """Test get_summary_stats with all clean repositories."""
        scanner = GitScanner()

        # Create clean repositories
        clean_repo1 = Mock()
        clean_repo1.changed_count = 0
        clean_repo1.ahead_count = 0
        clean_repo1.behind_count = 0
        clean_repo1.untracked_count = 0

        clean_repo2 = Mock()
        clean_repo2.changed_count = 0
        clean_repo2.ahead_count = 0
        clean_repo2.behind_count = 0
        clean_repo2.untracked_count = 0

        scanner.repositories = [clean_repo1, clean_repo2]

        result = scanner.get_summary_stats()

        assert result == {
            "total_repos": 2,
            "repos_with_changes": 0,
            "repos_ahead": 0,
            "repos_behind": 0,
            "repos_with_untracked": 0,
        }

    def test_get_summary_stats_all_dirty(self):
        """Test get_summary_stats with all dirty repositories."""
        scanner = GitScanner()

        # Create dirty repositories
        dirty_repo1 = Mock()
        dirty_repo1.changed_count = 2
        dirty_repo1.ahead_count = 1
        dirty_repo1.behind_count = 1
        dirty_repo1.untracked_count = 3

        dirty_repo2 = Mock()
        dirty_repo2.changed_count = 1
        dirty_repo2.ahead_count = 0
        dirty_repo2.behind_count = 2
        dirty_repo2.untracked_count = 1

        scanner.repositories = [dirty_repo1, dirty_repo2]

        result = scanner.get_summary_stats()

        assert result == {
            "total_repos": 2,
            "repos_with_changes": 2,
            "repos_ahead": 1,  # Only dirty_repo1 has ahead_count > 0
            "repos_behind": 2,
            "repos_with_untracked": 2,
        }
