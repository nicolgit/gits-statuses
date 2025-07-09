from importlib.metadata import version, PackageNotFoundError


def get_current_version() -> str:
    """
    Get the current installed version.
    Returns:
        str: Current version or 'unknown' if not found
    """
    try:
        return version("gitskan")
    except PackageNotFoundError:
        return "unknown"
