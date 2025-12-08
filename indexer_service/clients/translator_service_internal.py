"""
HTTP-клиент для отправки результатов индексации в translator_service (внутренний клиент).
"""

import requests
from logger import logger
from config import TRANSLATOR_SERVICE_URL


def send_result_to_translator(result: str):
    """
    Отправляет результат индексации в translator_service.

    Параметры
    ---------
    result : str
        JSON-строка с результатом индексации.
    """
    logger.info(f"Отправка результата индексации в translator_service: {result}")

    payload = {
        "result": result
    }

    try:
        response = requests.post(TRANSLATOR_SERVICE_URL, json=payload, timeout=10)
        response.raise_for_status()
        logger.info(
            f"Результат успешно отправлен в translator_service: "
            f"{response.json()}"
        )
    except Exception as e:
        logger.error(
            f"Ошибка при отправке результата в translator_service: {e}",
            exc_info=True
        )
        raise

