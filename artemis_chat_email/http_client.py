"""
HTTP-клиент, отправляющий данные в translator_service.
"""

import requests
from logger import logger
from config import TRANSLATOR_URL


def send_to_translator(message: dict):
    """
    Отправляет сообщение (чата или email) в translator_service.

    Параметры
    ---------
    message : dict
        Словарь, содержащий данные сообщения.

    Возвращает
    ----------
    dict
        Ответ translator_service.
    """
    logger.info(f"Отправка сообщения в translator_service: {message}")

    response = requests.post(TRANSLATOR_URL, json=message)
    response.raise_for_status()

    return response.json()
