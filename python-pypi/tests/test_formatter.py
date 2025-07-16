"""
Unit tests for the TableFormatter class.
"""

from unittest.mock import Mock

from src.git_tools import TableFormatter


class TestTableFormatterRepositories:
    """Tests for repository table formatting."""

    def test_format_repositories_empty_list(self):
        """Test format_repositories with empty list."""
        result = TableFormatter.format_repositories([])
        assert result == "No Git repositories found."

    def test_format_repositories_standard_view_no_changes(self):
        """Test format_repositories in standard view with no changes."""
        # Create mock repositories with no changes
        clean_repo = Mock()
        clean_repo.name = "clean-repo"
        clean_repo.has_changes.return_value = False

        repositories = [clean_repo]
        result = TableFormatter.format_repositories(repositories, show_url=False)

        assert (
            result
            == "No Git repositories with changes found. Use --detailed to see all repositories."
        )

    def test_format_repositories_standard_view_with_changes(self):
        """Test format_repositories in standard view with changes."""
        # Create mock repository with changes
        dirty_repo = Mock()
        dirty_repo.name = "dirty-repo"
        dirty_repo.branch = "main"
        dirty_repo.ahead_count = 2
        dirty_repo.behind_count = 1
        dirty_repo.changed_count = 3
        dirty_repo.untracked_count = 1
        dirty_repo.has_changes.return_value = True

        repositories = [dirty_repo]
        result = TableFormatter.format_repositories(repositories, show_url=False)

        lines = result.split("\n")
        assert len(lines) >= 3  # header, separator, at least one row
        assert "Repository" in lines[0]
        assert "Branch" in lines[0]
        assert "Ahead" in lines[0]
        assert "Behind" in lines[0]
        assert "Changed" in lines[0]
        assert "Untracked" in lines[0]
        assert "Remote URL" not in lines[0]  # Should not show URL in standard view

        # Check that repo data is present
        assert "dirty-repo" in result
        assert "main" in result
        assert "2" in result  # ahead count
        assert "1" in result  # behind count
        assert "3" in result  # changed count

    def test_format_repositories_detailed_view(self):
        """Test format_repositories in detailed view."""
        # Create mock repository
        repo = Mock()
        repo.name = "test-repo"
        repo.branch = "feature"
        repo.ahead_count = 1
        repo.behind_count = 0
        repo.changed_count = 2
        repo.untracked_count = 1
        repo.total_commits = 42
        repo.status = "↑1 ~2 ?1"
        repo.remote_url = "https://github.com/user/test-repo.git"

        repositories = [repo]
        result = TableFormatter.format_repositories(repositories, show_url=True)

        lines = result.split("\n")
        assert len(lines) >= 3  # header, separator, at least one row
        assert "Repository" in lines[0]
        assert "Branch" in lines[0]
        assert "Total Commits" in lines[0]
        assert "Status" in lines[0]
        assert "Remote URL" in lines[0]

        # Check that all repo data is present
        assert "test-repo" in result
        assert "feature" in result
        assert "42" in result  # total commits
        assert "↑1 ~2 ?1" in result  # status
        assert "https://github.com/user/test-repo.git" in result

    def test_format_repositories_mixed_states(self):
        """Test format_repositories with repositories in different states."""
        # Clean repo
        clean_repo = Mock()
        clean_repo.name = "clean-repo"
        clean_repo.branch = "main"
        clean_repo.ahead_count = 0
        clean_repo.behind_count = 0
        clean_repo.changed_count = 0
        clean_repo.untracked_count = 0
        clean_repo.total_commits = 10
        clean_repo.status = "Clean"
        clean_repo.remote_url = "https://github.com/user/clean-repo.git"

        # Dirty repo
        dirty_repo = Mock()
        dirty_repo.name = "dirty-repo"
        dirty_repo.branch = "develop"
        dirty_repo.ahead_count = 3
        dirty_repo.behind_count = 2
        dirty_repo.changed_count = 5
        dirty_repo.untracked_count = 2
        dirty_repo.total_commits = 25
        dirty_repo.status = "↑3 ↓2 ~5 ?2"
        dirty_repo.remote_url = "https://github.com/user/dirty-repo.git"

        repositories = [clean_repo, dirty_repo]
        result = TableFormatter.format_repositories(repositories, show_url=True)

        lines = result.split("\n")
        assert len(lines) >= 4  # header, separator, two rows

        # Check that both repos are present
        assert "clean-repo" in result
        assert "dirty-repo" in result
        assert "Clean" in result
        assert "↑3 ↓2 ~5 ?2" in result

    def test_format_repositories_column_width_calculation(self):
        """Test that column widths are calculated correctly."""
        # Create repos with different name lengths
        short_repo = Mock()
        short_repo.name = "a"
        short_repo.branch = "main"
        short_repo.ahead_count = 0
        short_repo.behind_count = 0
        short_repo.changed_count = 0
        short_repo.untracked_count = 0
        short_repo.total_commits = 1
        short_repo.status = "Clean"
        short_repo.remote_url = "https://github.com/user/a.git"

        long_repo = Mock()
        long_repo.name = "very-long-repository-name"
        long_repo.branch = "feature-branch"
        long_repo.ahead_count = 10
        long_repo.behind_count = 5
        long_repo.changed_count = 15
        long_repo.untracked_count = 8
        long_repo.total_commits = 100
        long_repo.status = "↑10 ↓5 ~15 ?8"
        long_repo.remote_url = "https://github.com/user/very-long-repository-name.git"

        repositories = [short_repo, long_repo]
        result = TableFormatter.format_repositories(repositories, show_url=True)

        lines = result.split("\n")
        header_line = lines[0]
        separator_line = lines[1]

        # Check that separator line matches header length
        assert len(separator_line) == len(header_line)

        # Check that longer name is accommodated
        assert "very-long-repository-name" in result
        assert "feature-branch" in result

    def test_format_repositories_empty_values_handling(self):
        """Test handling of empty/zero values in formatting."""
        # Repo with some zero values
        repo = Mock()
        repo.name = "test-repo"
        repo.branch = "main"
        repo.ahead_count = 0  # Should display as empty
        repo.behind_count = 2  # Should display as "2"
        repo.changed_count = 0  # Should display as empty
        repo.untracked_count = 1  # Should display as "1"
        repo.total_commits = 20
        repo.status = "↓2 ?1"
        repo.remote_url = "https://github.com/user/test-repo.git"

        repositories = [repo]
        result = TableFormatter.format_repositories(repositories, show_url=True)

        lines = result.split("\n")
        data_line = lines[2]  # Skip header and separator

        # Check that zero values are displayed as empty strings
        # This is a bit tricky to test directly, but we can check the structure
        assert "test-repo" in data_line
        assert "main" in data_line
        assert "2" in data_line  # behind count
        assert "1" in data_line  # untracked count
        assert "20" in data_line  # total commits


class TestTableFormatterSummary:
    """Tests for summary statistics formatting."""

    def test_format_summary_basic(self):
        """Test format_summary with basic statistics."""
        stats = {
            "total_repos": 5,
            "repos_with_changes": 2,
            "repos_ahead": 1,
            "repos_behind": 1,
            "repos_with_untracked": 3,
        }

        result = TableFormatter.format_summary(stats)

        lines = result.split("\n")
        assert len(lines) == 7
        assert lines[0] == ""  # First line is empty
        assert lines[1] == "Summary:"
        assert "Total repositories: 5" in lines[2]
        assert "Repositories with changes: 2" in lines[3]
        assert "Repositories ahead of remote: 1" in lines[4]
        assert "Repositories behind remote: 1" in lines[5]
        assert "Repositories with untracked files: 3" in lines[6]

    def test_format_summary_zero_values(self):
        """Test format_summary with zero values."""
        stats = {
            "total_repos": 0,
            "repos_with_changes": 0,
            "repos_ahead": 0,
            "repos_behind": 0,
            "repos_with_untracked": 0,
        }

        result = TableFormatter.format_summary(stats)

        lines = result.split("\n")
        assert "Total repositories: 0" in lines[2]
        assert "Repositories with changes: 0" in lines[3]
        assert "Repositories ahead of remote: 0" in lines[4]
        assert "Repositories behind remote: 0" in lines[5]
        assert "Repositories with untracked files: 0" in lines[6]

    def test_format_summary_large_numbers(self):
        """Test format_summary with large numbers."""
        stats = {
            "total_repos": 1000,
            "repos_with_changes": 999,
            "repos_ahead": 500,
            "repos_behind": 300,
            "repos_with_untracked": 700,
        }

        result = TableFormatter.format_summary(stats)

        assert "Total repositories: 1000" in result
        assert "Repositories with changes: 999" in result
        assert "Repositories ahead of remote: 500" in result
        assert "Repositories behind remote: 300" in result
        assert "Repositories with untracked files: 700" in result


class TestTableFormatterIntegration:
    """Integration tests for TableFormatter."""

    def test_format_repositories_standard_vs_detailed(self):
        """Test difference between standard and detailed formatting."""
        # Create repository with changes
        repo = Mock()
        repo.name = "test-repo"
        repo.branch = "main"
        repo.ahead_count = 1
        repo.behind_count = 0
        repo.changed_count = 2
        repo.untracked_count = 1
        repo.total_commits = 50
        repo.status = "↑1 ~2 ?1"
        repo.remote_url = "https://github.com/user/test-repo.git"
        repo.has_changes.return_value = True

        repositories = [repo]

        # Standard view
        standard_result = TableFormatter.format_repositories(
            repositories, show_url=False
        )

        # Detailed view
        detailed_result = TableFormatter.format_repositories(
            repositories, show_url=True
        )

        # Standard view should not have URL or total commits
        assert "Remote URL" not in standard_result
        assert "Total Commits" not in standard_result
        assert "Status" not in standard_result

        # Detailed view should have URL and total commits
        assert "Remote URL" in detailed_result
        assert "Total Commits" in detailed_result
        assert "Status" in detailed_result
        assert "https://github.com/user/test-repo.git" in detailed_result
        assert "50" in detailed_result
        assert "↑1 ~2 ?1" in detailed_result
