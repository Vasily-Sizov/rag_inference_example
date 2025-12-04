"""
Главное FastAPI приложение для file_service.

Предоставляет эндпоинты для получения списка файлов и их содержимого.
"""

from fastapi import FastAPI, HTTPException
from file_reader import list_available_files, read_file
from logger import logger

app = FastAPI(title="File Service")


@app.on_event("startup")
async def startup():
    logger.info("File service started.")


@app.get("/files")
def get_files():
    """
    Возвращает список доступных файлов в хранилище.

    Returns
    -------
    list
        Список имен файлов.
    """
    return list_available_files()


@app.get("/file/{name}")
def get_file(name: str):
    """
    Возвращает содержимое указанного файла.

    Parameters
    ----------
    name : str
        Имя файла для получения.

    Returns
    -------
    str
        Содержимое файла.

    Raises
    ------
    HTTPException(404)
        Если файл не существует.
    """
    try:
        return read_file(name)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
