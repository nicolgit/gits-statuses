"""
Git repository information extraction module.
"""

import subprocess
from pathlib import Path


class GitRepository:
    """
    Represents a Git repository with its basic information.
    Attributes:
        path (Path): The path to the repository.
        name (str): The name of the repository.
        is_valid (bool): Whether the repository is valid.
        branch (str): The current branch of the repository.
        remote_url (str): The remote URL of the repository.
        ahead_count (int): The number of commits ahead of the remote.
        behind_count (int): The number of commits behind the remote.
        changed_count (int): The number of changed files.
        untracked_count (int): The number of untracked files.
        total_commits (int): The total number of commits in the repository.
        status (str): The summary of the repository status.
    """

    def __init__(self, path: str):
        self.path = Path(path)
        self.name = self.path.name
        self.is_valid = self._is_git_repository()

        if self.is_valid:
            self.branch = self._get_current_branch()
            self.remote_url = self._get_remote_url()
            self.ahead_count = self._get_ahead_count()
            self.behind_count = self._get_behind_count()
            self.changed_count = self._get_changed_count()
            self.untracked_count = self._get_untracked_count()
            self.total_commits = self._get_total_commits()
            self.status = self._get_status_summary()
        else:
            self.branch = "Unknown"
            self.remote_url = "No remote"
            self.ahead_count = 0
            self.behind_count = 0
            self.changed_count = 0
            self.untracked_count = 0
            self.total_commits = 0
            self.status = "Invalid"

    def _is_git_repository(self) -> bool:
        """
        Check if the directory is a valid Git repository.
        Returns:
            bool: True if the directory is a valid Git repository, False otherwise.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return False

    def _get_current_branch(self) -> str:
        """
        Get the current branch name.
        Returns:
            str: The current branch name.
        """
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                return branch if branch else "HEAD detached"
            return "Unknown"
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return "Unknown"

    def _get_remote_url(self) -> str:
        """
        Get the remote origin URL.
        Returns:
            str: The remote origin URL.
        """
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "No remote"
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
        ):
            return "No remote"

    def _get_ahead_count(self) -> int:
        """
        Get the number of commits ahead of remote.
        Returns:
            int: The number of commits ahead of remote.
        """
        try:
            # First check if we have a remote tracking branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "@{u}"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return 0  # No upstream branch

            upstream = result.stdout.strip()

            # Get the count of commits ahead
            result = subprocess.run(
                ["git", "rev-list", "--count", f"{upstream}..HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            ValueError,
        ):
            return 0

    def _get_behind_count(self) -> int:
        """
        Get the number of commits behind remote.
        Returns:
            int: The number of commits behind remote.
        """
        try:
            # First check if we have a remote tracking branch
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "@{u}"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return 0  # No upstream branch

            upstream = result.stdout.strip()

            # Get the count of commits behind
            result = subprocess.run(
                ["git", "rev-list", "--count", f"HEAD..{upstream}"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            ValueError,
        ):
            return 0

    def _get_changed_count(self) -> int:
        """
        Get the number of changed files (includes all files from git status --porcelain).
        Returns:
            int: The number of changed files.
        """
        try:
            # Get git status porcelain output
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if not lines or lines == [""]:
                    return 0

                # Count all files (PowerShell approach - includes untracked files)
                return len(lines)
            return 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            ValueError,
        ):
            return 0

    def _get_untracked_count(self) -> int:
        """
        Get the number of untracked files.
        Returns:
            int: The number of untracked files.
        """
        try:
            # Get git status porcelain output
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if not lines or lines == [""]:
                    return 0

                # Count untracked files
                untracked_count = 0
                for line in lines:
                    if len(line) >= 2 and line[:2] == "??":
                        untracked_count += 1

                return untracked_count
            return 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            ValueError,
        ):
            return 0

    def _get_total_commits(self) -> int:
        """
        Get the total number of commits in the repository.
        Returns:
            int: The total number of commits in the repository.
        """
        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (
            subprocess.TimeoutExpired,
            subprocess.SubprocessError,
            FileNotFoundError,
            ValueError,
        ):
            return 0

    def _get_status_summary(self) -> str:
        """
        Get a summary of the repository status.
        Returns:
            str: The summary of the repository status.
        """
        status_parts = []

        if self.ahead_count > 0:
            status_parts.append(f"↑{self.ahead_count}")

        if self.behind_count > 0:
            status_parts.append(f"↓{self.behind_count}")

        if self.changed_count > 0:
            status_parts.append(f"~{self.changed_count}")

        if self.untracked_count > 0:
            status_parts.append(f"?{self.untracked_count}")

        if not status_parts:
            return "Clean"

        return " ".join(status_parts)

    def has_changes(self) -> bool:
        """
        Check if the repository has any changes.
        Returns:
            bool: True if the repository has any changes, False otherwise.
        """
        return (
            self.ahead_count > 0
            or self.behind_count > 0
            or self.changed_count > 0
            or self.untracked_count > 0
        )
