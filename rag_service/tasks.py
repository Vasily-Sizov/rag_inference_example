"""
TaskIQ-задачи для rag_service.

Обрабатывают сообщения, выполняют векторный поиск и отправляют
ответы в translator_service.
"""

import json
from taskiq_redis import ListQueueBroker
from config import TASKIQ_BROKER_URL, QUEUE_CHATS, QUEUE_EMAIL
from vector_search import search_knn
from clients.translator_service_internal import send_result_to_translator
from logger import logger

broker = ListQueueBroker(TASKIQ_BROKER_URL)


@broker.task
def process_vector_message(message: str, source_queue: str):
    """
    Обрабатывает сообщение из Redis: декодирует вектор,
    делает поиск в OpenSearch и отправляет результат в translator_service.

    Параметры
    ---------
    message : str
        JSON-строка со списком чисел (вектор запроса).
    source_queue : str
        Имя очереди Redis, из которой пришло сообщение (chats или email).
    """
    logger.info(f"Получено сообщение для обработки из {source_queue}: {message}")

    vector = json.loads(message)
    result = search_knn(vector)

    response_text = (
        f"Документ: {result['doc_id']}, "
        f"фрагмент #{result['chunk_id']}, "
        f"текст: {result['content']}"
    )

    if source_queue not in [QUEUE_CHATS, QUEUE_EMAIL]:
        logger.warning(
            f"Неожиданная очередь-источник: {source_queue}, "
            f"ответ не отправлен."
        )
        return

    logger.info(
        f"Отправка ответа в translator_service из очереди {source_queue}"
    )
    send_result_to_translator(source_queue, response_text)

