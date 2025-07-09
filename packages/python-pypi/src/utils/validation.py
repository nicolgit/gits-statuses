import subprocess
import sys
from pathlib import Path


def check_git_availability() -> bool:
    """
    Check if Git is available in the system.
    Returns:
        bool: True if Git is available, False otherwise.
    """
    try:
        subprocess.run(["git", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def validate_path(path_str: str) -> Path:
    """
    Validate and return a Path object.
    Args:
        path_str (str): The path to validate.
    Returns:
        Path: The validated path.
    """
    path = Path(path_str)
    if not path.exists():
        print(f"Error: Path '{path_str}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Path '{path_str}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    return path
