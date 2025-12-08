"""
HTTP-клиент для отправки результатов в translator_service (внутренний клиент).
"""

import requests
from logger import logger
from config import TRANSLATOR_SERVICE_URL


def send_result_to_translator(source_queue: str, result: str):
    """
    Отправляет результат обработки в translator_service.

    Параметры
    ---------
    source_queue : str
        Имя очереди Redis, из которой пришло сообщение (chats или email).
    result : str
        Текст результата обработки.
    """
    logger.info(
        f"Отправка результата в translator_service из очереди "
        f"{source_queue}: {result}"
    )

    payload = {
        "source_queue": source_queue,
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

