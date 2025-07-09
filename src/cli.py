"""
Main CLI entry point for gitskan.
"""

import argparse
import sys

from git_tools import GitScanner, TableFormatter
from utils import (
    check_git_availability,
    print_error,
    validate_path,
    get_current_version,
)

__version__ = get_current_version()


def create_parser() -> argparse.ArgumentParser:
    """
    Create the argument parser.
    Returns:
        argparse.ArgumentParser: The argument parser.
    """
    parser = argparse.ArgumentParser(
        prog="gsk",
        description="Git repository status scanner - Displays status information for Git repositories",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "--path",
        default=".",
        help="Directory to scan for Git repositories (default: current directory)",
    )
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information including remote URLs and total commits",
    )

    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    # Check if Git is available
    if not check_git_availability():
        print_error(
            "Git is not installed or not in PATH. Please install Git to use this tool."
        )
        return 1

    # Validate the path
    validate_path(args.path)

    try:
        # Scan for repositories
        scanner = GitScanner(args.path)
        repositories = scanner.scan()

        # Sort repositories by name
        repositories.sort(key=lambda repo: repo.name.lower())

        # Display results
        print(f"\nFound {len(repositories)} Git repositories:\n")
        table = TableFormatter.format_repositories(repositories, show_url=args.detailed)
        print(table)

        # Summary
        if repositories:
            stats = scanner.get_summary_stats()
            summary = TableFormatter.format_summary(stats)
            print(summary)
        else:
            print("\nNo Git repositories found in the specified directory.")

        return 0

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print_error(f"An error occurred: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
