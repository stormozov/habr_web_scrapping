import json
import os
from datetime import datetime


def save_data_to_json(data: list[dict[str, str]], file_name: str) -> None:
    """Saves data to a json file.

    Args:
        data (list[dict[str, str]]): The data to save in the json file.
        file_name (str): The name of the file to save the data to.

    Returns:
        None

    Raises:
        TypeError: If data is not a list or if file_name is not a string.
        ValueError: If data is an empty list or if  is an empty string.
    """
    file_name_base: str = os.path.basename(file_name)

    if not isinstance(data, list):
        raise TypeError('Data must be a list')
    if not isinstance(file_name, str):
        raise TypeError('File name must be a string')
    if not file_name:
        raise ValueError('File name cannot be empty')
    if not data:
        raise ValueError('Data cannot be empty')
    if '.' in file_name_base:
        raise ValueError('File name must not contain extension or dots. '
                         'The file extension will be added automatically')

    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    with open(f'{file_name}_{timestamp}.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
