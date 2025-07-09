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

# Import shared utilities
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'shared'))
from git_tools.git_repository import GitRepository


class GitScanner:
    """Scans directories for Git repositories"""

    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path).resolve()
        self.repositories: List[GitRepository] = []

    def scan(self) -> List[GitRepository]:
        """Scan the directory for Git repositories"""

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


parser = argparse.ArgumentParser(
    description="Git Repository Status Scanner - Displays basic information for all Git repositories"
)
parser.add_argument(
    "path",
    nargs="?",
    default=str(Path.home() / "GitHub"),
    help="Path to scan for Git repositories (default: ~/GitHub)",
)
parser.add_argument(
    "--detailed",
    action="store_true",
    help="Show detailed information including remote URLs",
)
args = parser.parse_args()

# Use the parsed path argument
scan_path = Path(args.path)

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

        # Use shared utilities for status summary if needed
        status_summary = repo.get_status_summary()
        print(f"{line} | href={repo.remote_url} {FONT}")

except KeyboardInterrupt:
    print("\nOperation cancelled by user.")
    sys.exit(1)
except Exception as e:
    print(f"An error occurred: {e}", file=sys.stderr)
    sys.exit(1)

print("🔄 Refresh | refresh=true")