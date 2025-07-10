"""
Pytest configuration and fixtures for gitskan tests.
"""

import pytest
from unittest.mock import Mock, patch
import sys

from src.git_tools import GitRepository, GitScanner


@pytest.fixture
def mock_git_repository():
    """Create a mock GitRepository instance."""
    repo = Mock(spec=GitRepository)
    repo.name = "test-repo"
    repo.path = "/path/to/test-repo"
    repo.branch = "main"
    repo.ahead = 0
    repo.behind = 0
    repo.changed_files = 0
    repo.untracked_files = 0
    repo.total_commits = 42
    repo.remote_url = "https://github.com/user/test-repo.git"
    repo.is_clean = True
    repo.status = "Clean"
    return repo


@pytest.fixture
def mock_git_scanner():
    """Create a mock GitScanner instance."""
    scanner = Mock(spec=GitScanner)
    scanner.base_path = "/path/to/scan"
    return scanner


@pytest.fixture
def sample_repositories():
    """Create sample repository data for tests."""
    repos = []

    clean_repo = Mock(spec=GitRepository)
    clean_repo.name = "clean-repo"
    clean_repo.path = "/path/to/clean-repo"
    clean_repo.branch = "main"
    clean_repo.ahead = 0
    clean_repo.behind = 0
    clean_repo.changed_files = 0
    clean_repo.untracked_files = 0
    clean_repo.total_commits = 10
    clean_repo.remote_url = "https://github.com/user/clean-repo.git"
    clean_repo.is_clean = True
    clean_repo.status = "Clean"
    repos.append(clean_repo)

    dirty_repo = Mock(spec=GitRepository)
    dirty_repo.name = "dirty-repo"
    dirty_repo.path = "/path/to/dirty-repo"
    dirty_repo.branch = "feature-branch"
    dirty_repo.ahead = 2
    dirty_repo.behind = 1
    dirty_repo.changed_files = 3
    dirty_repo.untracked_files = 2
    dirty_repo.total_commits = 25
    dirty_repo.remote_url = "https://github.com/user/dirty-repo.git"
    dirty_repo.is_clean = False
    dirty_repo.status = "Dirty"
    repos.append(dirty_repo)

    return repos


@pytest.fixture
def mock_subprocess_run():
    """Mock subprocess.run for git commands."""
    with patch("subprocess.run") as mock_run:
        # Default successful git command
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "main"
        mock_run.return_value.stderr = ""
        yield mock_run


@pytest.fixture
def mock_os_path_exists():
    """Mock os.path.exists for path validation."""
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        yield mock_exists


@pytest.fixture
def mock_os_path_isdir():
    """Mock os.path.isdir for directory validation."""
    with patch("os.path.isdir") as mock_isdir:
        mock_isdir.return_value = True
        yield mock_isdir


@pytest.fixture
def mock_os_walk():
    """Mock os.walk for directory traversal."""
    with patch("os.walk") as mock_walk:
        mock_walk.return_value = [
            ("/path/to/scan", ["repo1", "repo2"], []),
            ("/path/to/scan/repo1", [".git"], ["file1.txt"]),
            ("/path/to/scan/repo2", [".git"], ["file2.txt"]),
        ]
        yield mock_walk


@pytest.fixture
def mock_sys_argv():
    """Mock sys.argv for CLI argument testing."""

    def _mock_argv(args):
        with patch.object(sys, "argv", args):
            yield

    return _mock_argv


@pytest.fixture
def mock_check_git_availability():
    """Mock git availability check."""
    with patch("utils.validation.check_git_availability") as mock_check:
        mock_check.return_value = True
        yield mock_check


@pytest.fixture
def mock_validate_path():
    """Mock path validation."""
    with patch("utils.validation.validate_path") as mock_validate:
        mock_validate.return_value = None
        yield mock_validate


@pytest.fixture
def mock_get_current_version():
    """Mock version retrieval."""
    with patch("utils.version.get_current_version") as mock_version:
        mock_version.return_value = "1.0.0"
        yield mock_version


@pytest.fixture
def temp_git_repo(tmp_path):
    """Create a temporary git repository for integration tests."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Create .git directory
    git_dir = repo_path / ".git"
    git_dir.mkdir()

    # Create some dummy files
    (repo_path / "README.md").write_text("# Test Repository")
    (repo_path / "main.py").write_text("print('Hello, World!')")

    return str(repo_path)


def assert_table_format(table_output, expected_repos):
    """Helper function to assert table formatting."""
    lines = table_output.strip().split("\n")

    # Check header is present
    assert any("Repository" in line for line in lines)
    assert any("Branch" in line for line in lines)

    # Check repository names are present
    for repo in expected_repos:
        assert any(repo.name in line for line in lines)


def assert_summary_format(summary_output, expected_stats):
    """Helper function to assert summary formatting."""
    lines = summary_output.strip().split("\n")

    assert any("Summary" in line for line in lines)

    # Check statistics are present
    if "total" in expected_stats:
        assert any(str(expected_stats["total"]) in line for line in lines)
    if "clean" in expected_stats:
        assert any(str(expected_stats["clean"]) in line for line in lines)
    if "dirty" in expected_stats:
        assert any(str(expected_stats["dirty"]) in line for line in lines)
