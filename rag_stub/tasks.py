"""
TaskIQ-задачи для rag_stub.

Обрабатывают сообщения, выполняют векторный поиск и отправляют
ответы обратно в Artemis.
"""

import json
from taskiq_redis import ListQueueBroker
from config import TASKIQ_BROKER_URL, CHAT_OUT_QUEUE, EMAIL_OUT_QUEUE, QUEUE_CHATS, QUEUE_EMAIL
from vector_search import search_knn
from artemis_producer import send_to_artemis
from logger import logger

broker = ListQueueBroker(TASKIQ_BROKER_URL)


@broker.task
def process_vector_message(message: str, source_queue: str):
    """
    Обрабатывает сообщение из Redis: декодирует вектор,
    делает поиск в OpenSearch и отправляет результат в Artemis OUT очередь.

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

    if source_queue == QUEUE_CHATS:
        out_queue = CHAT_OUT_QUEUE
    elif source_queue == QUEUE_EMAIL:
        out_queue = EMAIL_OUT_QUEUE
    else:
        logger.warning(f"Неожиданная очередь-источник: {source_queue}, ответ не отправлен.")
        return

    logger.info(f"Отправка ответа в Artemis очередь {out_queue}")
    send_to_artemis(out_queue, response_text)
