"""
Table formatting module for Git repository information.
"""

from typing import List
from git_tools import GitRepository


class TableFormatter:
    """Formats repository data into a table."""

    @staticmethod
    def format_repositories(
        repositories: List[GitRepository], show_url: bool = False
    ) -> str:
        """
        Format repositories into a table string.
        Args:
            repositories (List[GitRepository]): The list of repositories to format.
            show_url (bool): Whether to show the remote URL.
        Returns:
            str: The formatted table string.
        """
        if not repositories:
            return "No Git repositories found."

        # For standard view, filter out repositories with no activity
        display_repositories = repositories
        if not show_url:
            display_repositories = [repo for repo in repositories if repo.has_changes()]

            if not display_repositories:
                return "No Git repositories with changes found. Use --detailed to see all repositories."

        # Calculate column widths based on repositories to display
        max_name_width = max(len(repo.name) for repo in display_repositories)
        max_branch_width = max(len(repo.branch) for repo in display_repositories)
        max_ahead_width = max(
            len(str(repo.ahead_count)) if repo.ahead_count > 0 else 0
            for repo in display_repositories
        )
        max_ahead_width = max(max_ahead_width, len("Ahead"))
        max_behind_width = max(
            len(str(repo.behind_count)) if repo.behind_count > 0 else 0
            for repo in display_repositories
        )
        max_behind_width = max(max_behind_width, len("Behind"))
        max_changed_width = max(
            len(str(repo.changed_count)) if repo.changed_count > 0 else 0
            for repo in display_repositories
        )
        max_changed_width = max(max_changed_width, len("Changed"))
        max_untracked_width = max(
            len(str(repo.untracked_count)) if repo.untracked_count > 0 else 0
            for repo in display_repositories
        )
        max_untracked_width = max(max_untracked_width, len("Untracked"))

        # Ensure minimum widths
        name_width = max(max_name_width, len("Repository"))
        branch_width = max(max_branch_width, len("Branch"))
        ahead_width = max(max_ahead_width, len("Ahead"))
        behind_width = max(max_behind_width, len("Behind"))
        changed_width = max(max_changed_width, len("Changed"))
        untracked_width = max(max_untracked_width, len("Untracked"))

        if show_url:
            max_url_width = max(len(repo.remote_url) for repo in display_repositories)
            url_width = max(max_url_width, len("Remote URL"))
            max_commits_width = max(
                len(str(repo.total_commits)) for repo in display_repositories
            )
            commits_width = max(max_commits_width, len("Total Commits"))
            max_status_width = max(len(repo.status) for repo in display_repositories)
            status_width = max(max_status_width, len("Status"))

            # Create header with URL
            header = f"{'Repository':<{name_width}} | {'Branch':<{branch_width}} | {'Ahead':<{ahead_width}} | {'Behind':<{behind_width}} | {'Changed':<{changed_width}} | {'Untracked':<{untracked_width}} | {'Total Commits':<{commits_width}} | {'Status':<{status_width}} | {'Remote URL':<{url_width}}"
            separator = "-" * len(header)

            # Create rows with URL
            rows = []
            for repo in display_repositories:
                ahead_str = str(repo.ahead_count) if repo.ahead_count > 0 else ""
                behind_str = str(repo.behind_count) if repo.behind_count > 0 else ""
                changed_str = str(repo.changed_count) if repo.changed_count > 0 else ""
                untracked_str = (
                    str(repo.untracked_count) if repo.untracked_count > 0 else ""
                )
                row = f"{repo.name:<{name_width}} | {repo.branch:<{branch_width}} | {ahead_str:<{ahead_width}} | {behind_str:<{behind_width}} | {changed_str:<{changed_width}} | {untracked_str:<{untracked_width}} | {repo.total_commits:<{commits_width}} | {repo.status:<{status_width}} | {repo.remote_url:<{url_width}}"
                rows.append(row)
        else:
            # Create header without URL
            header = f"{'Repository':<{name_width}} | {'Branch':<{branch_width}} | {'Ahead':<{ahead_width}} | {'Behind':<{behind_width}} | {'Changed':<{changed_width}} | {'Untracked':<{untracked_width}}"
            separator = "-" * len(header)

            # Create rows without URL (only for active repositories)
            rows = []
            for repo in display_repositories:
                ahead_str = str(repo.ahead_count) if repo.ahead_count > 0 else ""
                behind_str = str(repo.behind_count) if repo.behind_count > 0 else ""
                changed_str = str(repo.changed_count) if repo.changed_count > 0 else ""
                untracked_str = (
                    str(repo.untracked_count) if repo.untracked_count > 0 else ""
                )
                row = f"{repo.name:<{name_width}} | {repo.branch:<{branch_width}} | {ahead_str:<{ahead_width}} | {behind_str:<{behind_width}} | {changed_str:<{changed_width}} | {untracked_str:<{untracked_width}}"
                rows.append(row)

        return "\n".join([header, separator] + rows)

    @staticmethod
    def format_summary(stats: dict) -> str:
        """
        Format summary statistics.
        Args:
            stats (dict): The statistics to format.
        Returns:
            str: The formatted summary string.
        """
        lines = [
            "\nSummary:",
            f"  Total repositories: {stats['total_repos']}",
            f"  Repositories with changes: {stats['repos_with_changes']}",
            f"  Repositories ahead of remote: {stats['repos_ahead']}",
            f"  Repositories behind remote: {stats['repos_behind']}",
            f"  Repositories with untracked files: {stats['repos_with_untracked']}",
        ]
        return "\n".join(lines)
