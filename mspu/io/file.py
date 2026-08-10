import json
import os
from pathlib import Path


def read_text(filepath: str | os.PathLike, encoding: str = 'utf-8') -> str:
    """
    Read the entire content of a text file.

    Parameters
    ----------
    filepath : str or os.PathLike
        Path to the file to read.
    encoding : str, optional
        File encoding (default is 'utf-8').

    Returns
    -------
    str
        The file content.
    """
    with open(filepath, 'r', encoding=encoding) as f:
        return f.read()


def write_text(
    filepath: str | os.PathLike,
    content: str,
    encoding: str = 'utf-8',
    mkdir: bool = False,
) -> Path:
    """
    Write text content to a file.

    Parameters
    ----------
    filepath : str or os.PathLike
        Path to the file to write.
    content : str
        Text content to write.
    encoding : str, optional
        File encoding (default is 'utf-8').
    mkdir : bool, optional
        Create the parent directory if it does not exist (default is False).

    Returns
    -------
    Path
        The path of the written file.
    """
    path = Path(filepath)
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding=encoding) as f:
        f.write(content)
    return path


def read_json(filepath: str | os.PathLike, encoding: str = 'utf-8') -> dict:
    """
    Read and parse a JSON file.

    Parameters
    ----------
    filepath : str or os.PathLike
        Path to the JSON file to read.
    encoding : str, optional
        File encoding (default is 'utf-8').

    Returns
    -------
    dict
        The parsed JSON content.
    """
    with open(filepath, 'r', encoding=encoding) as f:
        return json.load(f)


def write_json(
    filepath: str | os.PathLike,
    data: dict,
    encoding: str = 'utf-8',
    indent: int = 2,
    mkdir: bool = False,
) -> Path:
    """
    Serialize a dictionary to a JSON file.

    Parameters
    ----------
    filepath : str or os.PathLike
        Path to the JSON file to write.
    data : dict
        Data to serialize.
    encoding : str, optional
        File encoding (default is 'utf-8').
    indent : int, optional
        Indentation for the JSON output (default is 2).
    mkdir : bool, optional
        Create the parent directory if it does not exist (default is False).

    Returns
    -------
    Path
        The path of the written file.
    """
    path = Path(filepath)
    if mkdir:
        path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding=encoding) as f:
        json.dump(data, f, indent=indent)
    return path
