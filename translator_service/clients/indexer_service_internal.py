"""
HTTP-клиент для вызова сервиса indexer_service (внутренний клиент).
"""

import requests
from logger import logger
from config import INDEXER_URL


def trigger_indexing() -> dict:
    """
    Отправляет HTTP-запрос в сервис indexer_service для запуска индексации.

    Returns
    -------
    dict
        Ответ сервера indexer_service.
    """
    logger.info(f"Отправка запроса на индексацию: {INDEXER_URL}")

    try:
        response = requests.post(INDEXER_URL, timeout=300)  # 5 минут таймаут для индексации
        response.raise_for_status()
        data = response.json()
        logger.info(f"Индексация завершена. Ответ сервиса: {data}")
        return data
    except Exception as e:
        logger.error(f"Ошибка при вызове indexer_service: {e}", exc_info=True)
        raise

