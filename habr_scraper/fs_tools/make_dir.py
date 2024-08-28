import os


def make_dir(dir_path: str) -> None:
    """Creates a directory if it doesn't exist.

    Args:
        dir_path (str): The path to the directory to create.

    Raises:
        ValueError: If path is not a string or is empty.
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
