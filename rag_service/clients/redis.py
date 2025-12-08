"""
Клиент Redis для rag_service.

Предоставляет функцию для получения подключения.
"""

import redis
from config import REDIS_HOST, REDIS_PORT
from logger import logger


def get_redis_client() -> redis.Redis:
    """
    Создаёт и возвращает подключение к Redis.

    Returns
    -------
    redis.Redis
        Подключённый клиент Redis.
    """
    logger.info(f"Подключение к Redis {REDIS_HOST}:{REDIS_PORT}")
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

