"""
Предоставляет функции для получения списка и чтения файлов из папки хранилища.
"""

import os
from config import BASE_DIR
from logger import logger


def list_available_files() -> list:
    """
    Возвращает список всех доступных файлов в директории хранилища.

    Returns
    -------
    list
        Список имен файлов, находящихся в BASE_DIR.
    """
    logger.info(f"Listing files in {BASE_DIR}")
    return os.listdir(BASE_DIR)


def read_file(name: str) -> str:
    """
    Читает текстовый файл из директории хранилища и возвращает его содержимое.

    Parameters
    ----------
    name : str
        Имя файла для чтения.

    Returns
    -------
    str
        Содержимое файла в виде обычного текста.

    Raises
    ------
    FileNotFoundError
        Если файл не существует.
    """
    path = os.path.join(BASE_DIR, name)
    logger.info(f"Reading file: {path}")

    with open(path, "r", encoding="utf-8") as f:
        return f.read()
