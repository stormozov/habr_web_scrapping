import os


def get_absolute_path(path_segments: list[str]) -> str:
    """Returns an absolute path from a list of path segments.

    Args:
        path_segments (list[str]): A list of path segments.

    Returns:
        An absolute path from the given path segments.
    """
    file_path = os.path.join(*path_segments)
    return os.path.abspath(file_path)
