"""
Unit tests for the GitRepository class.
"""

from unittest.mock import patch, Mock
import subprocess
from pathlib import Path

from git_tools import GitRepository


class TestGitRepositoryInit:
    """Tests for GitRepository initialization."""

    @patch("git_tools.repository.GitRepository._is_git_repository")
    def test_init_valid_repository(self, mock_is_git_repo):
        """Test initialization with valid git repository."""
        mock_is_git_repo.return_value = True

        with patch.object(
            GitRepository, "_get_current_branch", return_value="main"
        ), patch.object(
            GitRepository,
            "_get_remote_url",
            return_value="https://github.com/test/repo.git",
        ), patch.object(
            GitRepository, "_get_ahead_count", return_value=2
        ), patch.object(
            GitRepository, "_get_behind_count", return_value=1
        ), patch.object(
            GitRepository, "_get_changed_count", return_value=3
        ), patch.object(
            GitRepository, "_get_untracked_count", return_value=1
        ), patch.object(
            GitRepository, "_get_total_commits", return_value=42
        ), patch.object(
            GitRepository, "_get_status_summary", return_value="↑2 ↓1 ~3 ?1"
        ):
            repo = GitRepository("/path/to/repo")

            assert repo.path == Path("/path/to/repo")
            assert repo.name == "repo"
            assert repo.is_valid is True
            assert repo.branch == "main"
            assert repo.remote_url == "https://github.com/test/repo.git"
            assert repo.ahead_count == 2
            assert repo.behind_count == 1
            assert repo.changed_count == 3
            assert repo.untracked_count == 1
            assert repo.total_commits == 42
            assert repo.status == "↑2 ↓1 ~3 ?1"

    @patch("git_tools.repository.GitRepository._is_git_repository")
    def test_init_invalid_repository(self, mock_is_git_repo):
        """Test initialization with invalid git repository."""
        mock_is_git_repo.return_value = False

        repo = GitRepository("/path/to/non-repo")

        assert repo.path == Path("/path/to/non-repo")
        assert repo.name == "non-repo"
        assert repo.is_valid is False
        assert repo.branch == "Unknown"
        assert repo.remote_url == "No remote"
        assert repo.ahead_count == 0
        assert repo.behind_count == 0
        assert repo.changed_count == 0
        assert repo.untracked_count == 0
        assert repo.total_commits == 0
        assert repo.status == "Invalid"


class TestGitRepositoryValidation:
    """Tests for git repository validation."""

    @patch("git_tools.repository.subprocess.run")
    def test_is_git_repository_valid(self, mock_run):
        """Test _is_git_repository with valid repository."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "true"

        # Create repo instance without calling other methods
        repo = GitRepository.__new__(GitRepository)
        repo.path = Path("/path/to/repo")

        result = repo._is_git_repository()

        assert result is True
        mock_run.assert_called_once_with(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=repo.path,
            capture_output=True,
            text=True,
            timeout=5,
        )

    @patch("subprocess.run")
    def test_is_git_repository_invalid(self, mock_run):
        """Test _is_git_repository with invalid repository."""
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = "false"

        repo = GitRepository("/path/to/non-repo")
        result = repo._is_git_repository()

        assert result is False

    @patch("subprocess.run")
    def test_is_git_repository_timeout(self, mock_run):
        """Test _is_git_repository with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git"], 5)

        repo = GitRepository("/path/to/repo")
        result = repo._is_git_repository()

        assert result is False

    @patch("subprocess.run")
    def test_is_git_repository_file_not_found(self, mock_run):
        """Test _is_git_repository with git not found."""
        mock_run.side_effect = FileNotFoundError()

        repo = GitRepository("/path/to/repo")
        result = repo._is_git_repository()

        assert result is False


class TestGitRepositoryBranch:
    """Tests for branch information retrieval."""

    @patch("subprocess.run")
    def test_get_current_branch_success(self, mock_run):
        """Test _get_current_branch with successful result."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "main\n"

        repo = GitRepository("/path/to/repo")
        result = repo._get_current_branch()

        assert result == "main"

    @patch("subprocess.run")
    def test_get_current_branch_detached_head(self, mock_run):
        """Test _get_current_branch with detached HEAD."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""

        repo = GitRepository("/path/to/repo")
        result = repo._get_current_branch()

        assert result == "HEAD detached"

    @patch("subprocess.run")
    def test_get_current_branch_error(self, mock_run):
        """Test _get_current_branch with git error."""
        mock_run.return_value.returncode = 1

        repo = GitRepository("/path/to/repo")
        result = repo._get_current_branch()

        assert result == "Unknown"

    @patch("subprocess.run")
    def test_get_current_branch_timeout(self, mock_run):
        """Test _get_current_branch with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git"], 5)

        repo = GitRepository("/path/to/repo")
        result = repo._get_current_branch()

        assert result == "Unknown"


class TestGitRepositoryRemote:
    """Tests for remote URL retrieval."""

    @patch("subprocess.run")
    def test_get_remote_url_success(self, mock_run):
        """Test _get_remote_url with successful result."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "https://github.com/user/repo.git\n"

        repo = GitRepository("/path/to/repo")
        result = repo._get_remote_url()

        assert result == "https://github.com/user/repo.git"

    @patch("subprocess.run")
    def test_get_remote_url_no_remote(self, mock_run):
        """Test _get_remote_url with no remote."""
        mock_run.return_value.returncode = 1

        repo = GitRepository("/path/to/repo")
        result = repo._get_remote_url()

        assert result == "No remote"

    @patch("subprocess.run")
    def test_get_remote_url_timeout(self, mock_run):
        """Test _get_remote_url with timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired(["git"], 5)

        repo = GitRepository("/path/to/repo")
        result = repo._get_remote_url()

        assert result == "No remote"


class TestGitRepositoryCommitCounts:
    """Tests for commit count retrieval."""

    @patch("git_tools.repository.subprocess.run")
    def test_get_ahead_count_success(self, mock_run):
        """Test _get_ahead_count with successful result."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="origin/main\n"),  # upstream check
            Mock(returncode=0, stdout="3\n"),  # ahead count
        ]

        # Create repo instance without calling other methods
        repo = GitRepository.__new__(GitRepository)
        repo.path = Path("/path/to/repo")

        result = repo._get_ahead_count()

        assert result == 3

    @patch("subprocess.run")
    def test_get_ahead_count_no_upstream(self, mock_run):
        """Test _get_ahead_count with no upstream branch."""
        mock_run.return_value.returncode = 1

        repo = GitRepository("/path/to/repo")
        result = repo._get_ahead_count()

        assert result == 0

    @patch("git_tools.repository.subprocess.run")
    def test_get_behind_count_success(self, mock_run):
        """Test _get_behind_count with successful result."""
        mock_run.side_effect = [
            Mock(returncode=0, stdout="origin/main\n"),  # upstream check
            Mock(returncode=0, stdout="2\n"),  # behind count
        ]

        # Create repo instance without calling other methods
        repo = GitRepository.__new__(GitRepository)
        repo.path = Path("/path/to/repo")

        result = repo._get_behind_count()

        assert result == 2

    @patch("subprocess.run")
    def test_get_total_commits_success(self, mock_run):
        """Test _get_total_commits with successful result."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "42\n"

        repo = GitRepository("/path/to/repo")
        result = repo._get_total_commits()

        assert result == 42

    @patch("subprocess.run")
    def test_get_total_commits_error(self, mock_run):
        """Test _get_total_commits with git error."""
        mock_run.return_value.returncode = 1

        repo = GitRepository("/path/to/repo")
        result = repo._get_total_commits()

        assert result == 0


class TestGitRepositoryFileStatus:
    """Tests for file status retrieval."""

    @patch("subprocess.run")
    def test_get_changed_count_success(self, mock_run):
        """Test _get_changed_count with files."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = " M file1.txt\n?? file2.txt\nA  file3.txt\n"

        repo = GitRepository("/path/to/repo")
        result = repo._get_changed_count()

        assert result == 3

    @patch("subprocess.run")
    def test_get_changed_count_no_changes(self, mock_run):
        """Test _get_changed_count with no changes."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = ""

        repo = GitRepository("/path/to/repo")
        result = repo._get_changed_count()

        assert result == 0

    @patch("subprocess.run")
    def test_get_untracked_count_success(self, mock_run):
        """Test _get_untracked_count with untracked files."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = (
            " M file1.txt\n?? file2.txt\n?? file3.txt\nA  file4.txt\n"
        )

        repo = GitRepository("/path/to/repo")
        result = repo._get_untracked_count()

        assert result == 2

    @patch("subprocess.run")
    def test_get_untracked_count_no_untracked(self, mock_run):
        """Test _get_untracked_count with no untracked files."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = " M file1.txt\nA  file2.txt\n"

        repo = GitRepository("/path/to/repo")
        result = repo._get_untracked_count()

        assert result == 0


class TestGitRepositoryStatus:
    """Tests for status summary generation."""

    def test_get_status_summary_clean(self):
        """Test _get_status_summary with clean repository."""
        repo = GitRepository("/path/to/repo")
        repo.ahead_count = 0
        repo.behind_count = 0
        repo.changed_count = 0
        repo.untracked_count = 0

        result = repo._get_status_summary()

        assert result == "Clean"

    def test_get_status_summary_with_changes(self):
        """Test _get_status_summary with various changes."""
        repo = GitRepository("/path/to/repo")
        repo.ahead_count = 2
        repo.behind_count = 1
        repo.changed_count = 3
        repo.untracked_count = 1

        result = repo._get_status_summary()

        assert result == "↑2 ↓1 ~3 ?1"

    def test_get_status_summary_partial_changes(self):
        """Test _get_status_summary with partial changes."""
        repo = GitRepository("/path/to/repo")
        repo.ahead_count = 0
        repo.behind_count = 2
        repo.changed_count = 1
        repo.untracked_count = 0

        result = repo._get_status_summary()

        assert result == "↓2 ~1"

    def test_has_changes_true(self):
        """Test has_changes with repository that has changes."""
        repo = GitRepository("/path/to/repo")
        repo.ahead_count = 1
        repo.behind_count = 0
        repo.changed_count = 0
        repo.untracked_count = 0

        result = repo.has_changes()

        assert result is True

    def test_has_changes_false(self):
        """Test has_changes with clean repository."""
        repo = GitRepository("/path/to/repo")
        repo.ahead_count = 0
        repo.behind_count = 0
        repo.changed_count = 0
        repo.untracked_count = 0

        result = repo.has_changes()

        assert result is False
