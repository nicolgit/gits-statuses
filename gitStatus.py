#!/usr/bin/env PYTHONIOENCODING=UTF-8 /usr/local/bin/python3

"""
Git Repository Status Scanner

This script scans the current directory (or specified directory) for Git repositories
and displays a table with:
- Repository name
- Current branch
- Ahead count (commits ahead of remote)
- Behind count (commits behind remote)
- Changed files count (all files from git status - includes untracked files)
- Untracked files count
- Total commits count (shown only in detailed view)
- Status summary (shown only in detailed view)
- Remote URL (shown only in detailed view)
"""

# <xbar.title>GitStatus</xbar.title>
# <xbar.version>v1.0</xbar.version>
# <xbar.author>Tommaso Bucaioni</xbar.author>
# <xbar.author.github>Tommaso23</xbar.author.github>
# <xbar.desc>This script scans the current directory (or specified directory) for Git repositories and displays a table with data</xbar.desc>
# <xbar.image>http://www.hosted-somewhere/pluginimage</xbar.image>
# <xbar.dependencies>python3</xbar.dependencies>
# <xbar.abouturl>https://github.com/Tommaso23</xbar.abouturl>
# <xbar.parameter>--name="rootFolder"</xbar.parameter>

import os
import subprocess
import argparse
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any


class GitRepository:
    """Represents a Git repository with its basic information"""

    def __init__(self, path: str):
        self.path = Path(path)
        self.name = self.path.name
        self.branch = self._get_current_branch()
        self.remote_url = self._get_remote_url()
        self.ahead_count = self._get_ahead_count()
        self.behind_count = self._get_behind_count()
        self.changed_count = self._get_changed_count()
        self.untracked_count = self._get_untracked_count()
        self.is_valid = self._is_git_repository()

    def _is_git_repository(self) -> bool:
        """Check if the directory is a valid Git repository"""
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
        """Get the current branch name"""
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
        """Get the remote origin URL"""
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
        """Get the number of commits ahead of remote"""
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
        """Get the number of commits behind remote"""
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
        """Get the number of changed files (includes all files from git status --porcelain)"""
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
        """Get the number of untracked files"""
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
        """Get a summary of the repository status"""
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


class GitScanner:
    """Scans directories for Git repositories"""

    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path).resolve()
        self.repositories: List[GitRepository] = []

    def scan(self) -> List[GitRepository]:
        """Scan the directory for Git repositories"""

        # Check if the scan path itself is a Git repository

        """
        if self._is_directory_git_repo(self.scan_path):
            repo = GitRepository(str(self.scan_path))
            if repo.is_valid:
                self.repositories.append(repo)
        """
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
        """Quick check if directory contains a .git folder"""
        return (path / ".git").exists()


def check_git_availability() -> bool:
    """Check if Git is available in the system"""
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


# SwiftBar parameters for rendering
NAME_WIDTH = 18
BRANCH_WIDTH = 12
COUNT_WIDTH = 10

name = os.getenv("name", "GitHub")


def truncate(text, width):
    if len(text) > width:
        return text[: width - 3] + "..."
    return text.ljust(width)


FONT = "font=Menlo size=11"
print("📦 GitStatus")
print("---")

# Header (titoli colonna)
header = f"{'Repository':<{NAME_WIDTH}} {'Branch':<12}{'Ahead':<{COUNT_WIDTH}}{'Behind':<{COUNT_WIDTH}}{'Change':<{COUNT_WIDTH}}{'Untracked':<{COUNT_WIDTH}} | {FONT}"
print(header)
print("---")


scan_path = Path.home() / "GitHub"

parser = argparse.ArgumentParser(
    description="Git Repository Status Scanner - Displays basic information for all Git repositories"
)
parser.add_argument(
    "path",
    nargs="?",
    default=".",
    help="Path to scan for Git repositories (default: current directory)",
)
parser.add_argument(
    "--detailed",
    action="store_true",
    help="Show detailed information including remote URLs",
)
args = parser.parse_args()

# Check if Git is available
if not check_git_availability():
    print(
        "Error: Git is not installed or not in PATH. Please install Git to use this script.",
        file=sys.stderr,
    )
    sys.exit(1)
# Validate the path
if not scan_path.exists():
    print(f"Error: Path '{scan_path}' does not exist.", file=sys.stderr)
    sys.exit(1)
if not scan_path.is_dir():
    print(f"Error: Path '{scan_path}' is not a directory.", file=sys.stderr)
    sys.exit(1)
try:
    # Scan for repositories
    scanner = GitScanner(scan_path)
    repositories = scanner.scan()
    # Sort repositories by name
    repositories.sort(key=lambda repo: repo.name.lower())
    # Display results
    # print(f"\nFound {len(repositories)} Git repositories:\n")

    for repo in repositories:
        name = truncate(repo.name, 15)
        branch = truncate(repo.branch, 12)
        ahead = str(repo.ahead_count)
        behind = str(repo.behind_count)
        changed = str(repo.changed_count)
        untracked = str(repo.untracked_count)

        line = f"{name:<{NAME_WIDTH}} {branch:<12}{ahead:<{COUNT_WIDTH}}{behind:<{COUNT_WIDTH}}{changed:<{COUNT_WIDTH}}{untracked:<{COUNT_WIDTH}}"

        print(f"{line} | href={repo.remote_url} {FONT}")

except KeyboardInterrupt:
    print("\nOperation cancelled by user.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)

print("🔄 Refresh | refresh=true")
