"""
Логика определения назначения сообщения (chat/email/index)
и маршрутизация в соответствующие сервисы.
"""

from config import QUEUE_CHATS, QUEUE_EMAIL
from clients.redis import push_to_queue
from logger import logger
from clients.indexer_service_internal import trigger_indexing


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


def route_index_message(body: str):
    """
    Обрабатывает сообщение из очереди index.in и запускает индексацию.

    Параметры
    ---------
    body : str
        Содержимое сообщения (может содержать параметры индексации).
    """
    logger.info(f"Получен запрос на индексацию: {body}")
    try:
        trigger_indexing()
        logger.info("Индексация успешно запущена")
    except Exception as e:
        logger.error(f"Ошибка при запуске индексации: {e}", exc_info=True)
        raise
