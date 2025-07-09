"""
Git repository scanner module.
"""

from pathlib import Path
from typing import List

from git_tools.repository import GitRepository


class GitScanner:
    """Scans directories for Git repositories."""

    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path).resolve()
        self.repositories: List[GitRepository] = []

    def scan(self) -> List[GitRepository]:
        """Scan the directory for Git repositories."""
        print(f"Scanning for Git repositories in: {self.scan_path}")

        # Check if the scan path itself is a Git repository
        if self._is_directory_git_repo(self.scan_path):
            repo = GitRepository(str(self.scan_path))
            if repo.is_valid:
                self.repositories.append(repo)

        # Scan subdirectories
        try:
            for item in self.scan_path.iterdir():
                if item.is_dir() and not item.name.startswith("."):
                    if self._is_directory_git_repo(item):
                        repo = GitRepository(str(item))
                        if repo.is_valid:
                            self.repositories.append(repo)
        except PermissionError:
            print(f"Permission denied accessing: {self.scan_path}")

        return self.repositories

    def _is_directory_git_repo(self, path: Path) -> bool:
        """Quick check if directory contains a .git folder."""
        return (path / ".git").exists()

    def get_repositories_with_changes(self) -> List[GitRepository]:
        """Get only repositories that have changes."""
        return [repo for repo in self.repositories if repo.has_changes()]

    def get_summary_stats(self) -> dict:
        """Get summary statistics for all repositories."""
        total_repos = len(self.repositories)
        repos_with_changes = len(
            [repo for repo in self.repositories if repo.changed_count > 0]
        )
        repos_ahead = len([repo for repo in self.repositories if repo.ahead_count > 0])
        repos_behind = len(
            [repo for repo in self.repositories if repo.behind_count > 0]
        )
        repos_with_untracked = len(
            [repo for repo in self.repositories if repo.untracked_count > 0]
        )

        return {
            "total_repos": total_repos,
            "repos_with_changes": repos_with_changes,
            "repos_ahead": repos_ahead,
            "repos_behind": repos_behind,
            "repos_with_untracked": repos_with_untracked,
        }
