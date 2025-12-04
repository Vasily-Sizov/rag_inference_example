"""
HTTP-клиент для вызова сервиса indexer_stub.

Содержит функции для запуска операции индексации.
"""

import requests
from logger import logger
from config import INDEXER_URL


def trigger_indexing() -> dict:
    """
    Отправляет HTTP-запрос в сервис indexer_stub для запуска индексации.

    Returns
    -------
    dict
        Ответ сервера indexer_stub.
    """
    logger.info(f"Отправка запроса на индексацию: {INDEXER_URL}")

    response = requests.post(INDEXER_URL)

    response.raise_for_status()
    data = response.json()

    logger.info(f"Индексация завершена. Ответ сервиса: {data}")

    return data
