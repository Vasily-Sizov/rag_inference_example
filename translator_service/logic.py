"""
Логика определения назначения сообщения (chat/email)
и помещение его в соответствующую очередь Redis.
"""

from config import QUEUE_CHATS, QUEUE_EMAIL
from redis_client import push_to_queue
from logger import logger


def route_message(source_queue: str, body: str) -> str:
    """
    Определяет тип сообщения и направляет его в нужную очередь Redis.

    Параметры
    ---------
    source_queue : str
        Имя очереди Artemis, из которой пришло сообщение (chat.in или email.in).
    body : str
        Содержимое сообщения.

    Возвращает
    ----------
    str
        Название очереди Redis, куда было отправлено сообщение.
    """

    if source_queue == "chat.in":
        redis_queue = QUEUE_CHATS
    elif source_queue == "email.in":
        redis_queue = QUEUE_EMAIL
    else:
        logger.warning(f"Неизвестная очередь Artemis: {source_queue}. Сообщение игнорируется.")
        return "ignored"

    push_to_queue(redis_queue, body)

    logger.info(f"Сообщение направлено в Redis очередь: {redis_queue}")
    return redis_queue
