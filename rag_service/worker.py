"""
Воркер, читающий очереди Redis и отправляющий задачи в TaskIQ.
"""

import asyncio
from clients.redis import get_redis_client
from config import QUEUE_CHATS, QUEUE_EMAIL, TASKIQ_BROKER_URL
from tasks import broker, process_vector_message
from logger import logger


async def redis_poll_loop():
    """
    Основной цикл чтения из двух очередей Redis (chats, email).

    Каждое считанное сообщение отправляется в TaskIQ-задачу.
    """
    redis = get_redis_client()
    logger.info(
        f"Старт цикла чтения Redis очередей: {QUEUE_CHATS}, {QUEUE_EMAIL}"
    )

    while True:
        msg = redis.brpop([QUEUE_CHATS, QUEUE_EMAIL], timeout=1)
        if msg:
            queue_name, body = msg
            logger.info(f"Получено сообщение из Redis '{queue_name}': {body}")
            # Вызываем функцию напрямую (она синхронная)
            try:
                process_vector_message(body, queue_name)
            except Exception as e:
                logger.error(f"Ошибка при обработке сообщения: {e}")
        await asyncio.sleep(0.1)


def start_worker():
    """
    Запускает асинхронный цикл воркера.
    """
    logger.info("Запуск воркера rag_service...")
    asyncio.run(redis_poll_loop())


if __name__ == "__main__":
    start_worker()

