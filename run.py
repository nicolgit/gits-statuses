#!/usr/bin/env python3

"""
Git Repository Status Scanner

This script scans the current directory (or specified directory) for Git repositories
and displays a table with:
- Repository name
- Current branch
- Ahead count (commits ahead of remote)
- Behind count (commits behind remote)
- Changed files count (modified/added/deleted files)
- Untracked files count
- Total commits count (shown only in detailed view)
- Remote URL (shown only in detailed view)
"""

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
        self.total_commits = self._get_total_commits()
        self.is_valid = self._is_git_repository()
    
    def _is_git_repository(self) -> bool:
        """Check if the directory is a valid Git repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--is-inside-work-tree'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and result.stdout.strip() == 'true'
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False
    
    def _get_current_branch(self) -> str:
        """Get the current branch name"""
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                return branch if branch else "HEAD detached"
            return "Unknown"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return "Unknown"
    
    def _get_remote_url(self) -> str:
        """Get the remote origin URL"""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', 'remote.origin.url'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
            return "No remote"
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return "No remote"
    
    def _get_ahead_count(self) -> int:
        """Get the number of commits ahead of remote"""
        try:
            # First check if we have a remote tracking branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', '@{u}'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return 0  # No upstream branch
            
            upstream = result.stdout.strip()
            
            # Get the count of commits ahead
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'{upstream}..HEAD'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            return 0
    
    def _get_behind_count(self) -> int:
        """Get the number of commits behind remote"""
        try:
            # First check if we have a remote tracking branch
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', '@{u}'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                return 0  # No upstream branch
            
            upstream = result.stdout.strip()
            
            # Get the count of commits behind
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'HEAD..{upstream}'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            return 0
    
    def _get_changed_count(self) -> int:
        """Get the number of changed files (modified, added, deleted)"""
        try:
            # Get git status porcelain output
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if not lines or lines == ['']:
                    return 0
                
                # Count changed files (excluding untracked files)
                changed_count = 0
                for line in lines:
                    if len(line) >= 2:
                        # Check if file is modified/added/deleted (not untracked)
                        if line[:2] != '??':
                            changed_count += 1
                
                return changed_count
            return 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            return 0
    
    def _get_untracked_count(self) -> int:
        """Get the number of untracked files"""
        try:
            # Get git status porcelain output
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if not lines or lines == ['']:
                    return 0
                
                # Count untracked files
                untracked_count = 0
                for line in lines:
                    if len(line) >= 2 and line[:2] == '??':
                        untracked_count += 1
                
                return untracked_count
            return 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            return 0
    
    def _get_total_commits(self) -> int:
        """Get the total number of commits in the repository"""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
            return 0
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError, ValueError):
            return 0


class GitScanner:
    """Scans directories for Git repositories"""
    
    def __init__(self, scan_path: str = "."):
        self.scan_path = Path(scan_path).resolve()
        self.repositories: List[GitRepository] = []
    
    def scan(self) -> List[GitRepository]:
        """Scan the directory for Git repositories"""
        print(f"Scanning for Git repositories in: {self.scan_path}")
        
        # Check if the scan path itself is a Git repository
        if self._is_directory_git_repo(self.scan_path):
            repo = GitRepository(str(self.scan_path))
            if repo.is_valid:
                self.repositories.append(repo)
        
        # Scan subdirectories
        try:
            for item in self.scan_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    if self._is_directory_git_repo(item):
                        repo = GitRepository(str(item))
                        if repo.is_valid:
                            self.repositories.append(repo)
        except PermissionError:
            print(f"Permission denied accessing: {self.scan_path}")
        
        return self.repositories
    
    def _is_directory_git_repo(self, path: Path) -> bool:
        """Quick check if directory contains a .git folder"""
        return (path / '.git').exists()


class TableFormatter:
    """Formats repository data into a table"""
    
    @staticmethod
    def format_repositories(repositories: List[GitRepository], show_url: bool = False) -> str:
        """Format repositories into a table string"""
        if not repositories:
            return "No Git repositories found."
        
        # For standard view, filter out repositories with no activity
        display_repositories = repositories
        if not show_url:
            display_repositories = [
                repo for repo in repositories 
                if repo.ahead_count > 0 or repo.behind_count > 0 or repo.changed_count > 0 or repo.untracked_count > 0
            ]
            
            if not display_repositories:
                return "No Git repositories with changes found. Use --detailed to see all repositories."
        
        # Calculate column widths based on repositories to display
        max_name_width = max(len(repo.name) for repo in display_repositories)
        max_branch_width = max(len(repo.branch) for repo in display_repositories)
        max_ahead_width = max(len(str(repo.ahead_count)) if repo.ahead_count > 0 else 0 for repo in display_repositories)
        max_ahead_width = max(max_ahead_width, len("Ahead"))
        max_behind_width = max(len(str(repo.behind_count)) if repo.behind_count > 0 else 0 for repo in display_repositories)
        max_behind_width = max(max_behind_width, len("Behind"))
        max_changed_width = max(len(str(repo.changed_count)) if repo.changed_count > 0 else 0 for repo in display_repositories)
        max_changed_width = max(max_changed_width, len("Changed"))
        max_untracked_width = max(len(str(repo.untracked_count)) if repo.untracked_count > 0 else 0 for repo in display_repositories)
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
            max_commits_width = max(len(str(repo.total_commits)) for repo in display_repositories)
            commits_width = max(max_commits_width, len("Total Commits"))
            
            # Create header with URL
            header = f"{'Repository':<{name_width}} | {'Branch':<{branch_width}} | {'Ahead':<{ahead_width}} | {'Behind':<{behind_width}} | {'Changed':<{changed_width}} | {'Untracked':<{untracked_width}} | {'Total Commits':<{commits_width}} | {'Remote URL':<{url_width}}"
            separator = "-" * len(header)
            
            # Create rows with URL
            rows = []
            for repo in display_repositories:
                ahead_str = str(repo.ahead_count) if repo.ahead_count > 0 else ""
                behind_str = str(repo.behind_count) if repo.behind_count > 0 else ""
                changed_str = str(repo.changed_count) if repo.changed_count > 0 else ""
                untracked_str = str(repo.untracked_count) if repo.untracked_count > 0 else ""
                row = f"{repo.name:<{name_width}} | {repo.branch:<{branch_width}} | {ahead_str:<{ahead_width}} | {behind_str:<{behind_width}} | {changed_str:<{changed_width}} | {untracked_str:<{untracked_width}} | {repo.total_commits:<{commits_width}} | {repo.remote_url:<{url_width}}"
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
                untracked_str = str(repo.untracked_count) if repo.untracked_count > 0 else ""
                row = f"{repo.name:<{name_width}} | {repo.branch:<{branch_width}} | {ahead_str:<{ahead_width}} | {behind_str:<{behind_width}} | {changed_str:<{changed_width}} | {untracked_str:<{untracked_width}}"
                rows.append(row)
        
        return "\n".join([header, separator] + rows)


def check_git_availability() -> bool:
    """Check if Git is available in the system"""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Git Repository Status Scanner - Displays basic information for all Git repositories"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to scan for Git repositories (default: current directory)"
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information including remote URLs"
    )
    
    args = parser.parse_args()
    
    # Check if Git is available
    if not check_git_availability():
        print("Error: Git is not installed or not in PATH. Please install Git to use this script.", file=sys.stderr)
        sys.exit(1)
    
    # Validate the path
    scan_path = Path(args.path)
    if not scan_path.exists():
        print(f"Error: Path '{args.path}' does not exist.", file=sys.stderr)
        sys.exit(1)
    
    if not scan_path.is_dir():
        print(f"Error: Path '{args.path}' is not a directory.", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Scan for repositories
        scanner = GitScanner(args.path)
        repositories = scanner.scan()
        
        # Display results
        print(f"\nFound {len(repositories)} Git repositories:\n")
        table = TableFormatter.format_repositories(repositories, show_url=args.detailed)
        print(table)
        
        # Summary
        if repositories:
            print(f"\nSummary: {len(repositories)} Git repositories found")
        else:
            print("\nNo Git repositories found in the specified directory.")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()