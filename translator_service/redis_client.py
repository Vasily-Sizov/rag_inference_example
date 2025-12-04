"""
Клиент Redis для translator_service.

Предоставляет функции для записи сообщений в разные очереди.
"""

import redis
from config import REDIS_HOST, REDIS_PORT
from logger import logger


# Глобальное подключение к Redis
redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def push_to_queue(queue_name: str, message: str):
    """
    Добавляет сообщение в указанную очередь Redis.

    Параметры
    ---------
    queue_name : str
        Название очереди Redis.
    message : str
        Тело сообщения.

    Возвращает
    ----------
    int
        Новый размер списка после добавления элемента.
    """
    logger.info(f"Запись сообщения в очередь Redis '{queue_name}': {message}")
    return redis_client.lpush(queue_name, message)
