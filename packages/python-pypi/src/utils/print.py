import sys


def print_error(message: str) -> None:
    """
    Print an error message to stderr.
    Args:
        message (str): The error message to print.
    """
    print(f"Error: {message}", file=sys.stderr)


def print_info(message: str) -> None:
    """
    Print an info message to stdout.
    Args:
        message (str): The info message to print.
    """
    print(message)
