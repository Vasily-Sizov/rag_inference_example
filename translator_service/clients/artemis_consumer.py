"""
AMQP-консьюмер, слушающий очереди Artemis: chat.in, email.in, index.in.

При получении сообщения обрабатывает его в зависимости от типа очереди.
"""

from proton.handlers import MessagingHandler
from proton.reactor import Container
from config import (
    ARTEMIS_URL,
    ARTEMIS_QUEUE_CHAT_IN,
    ARTEMIS_QUEUE_EMAIL_IN,
    ARTEMIS_QUEUE_INDEX_IN,
)
from logger import logger
from logic import route_message, route_index_message
import threading


class ArtemisConsumer(MessagingHandler):
    """
    Консьюмер Artemis, который слушает три очереди одновременно:
    chat.in, email.in и index.in.

    Каждый пришедший AMQP-месседж обрабатывается в зависимости от типа очереди.
    """

    def __init__(self):
        super().__init__()
        logger.info("Инициализация Artemis consumer для chat.in + email.in + index.in")

    def on_start(self, event):
        """
        Подключение к Artemis и создание трех подписчиков.
        """
        logger.info("Подключение к Artemis...")
        conn = event.container.connect(ARTEMIS_URL)

        # Подписка на chat.in
        event.container.create_receiver(conn, ARTEMIS_QUEUE_CHAT_IN)
        logger.info(f"Подписка на очередь: {ARTEMIS_QUEUE_CHAT_IN}")

        # Подписка на email.in
        event.container.create_receiver(conn, ARTEMIS_QUEUE_EMAIL_IN)
        logger.info(f"Подписка на очередь: {ARTEMIS_QUEUE_EMAIL_IN}")

        # Подписка на index.in
        event.container.create_receiver(conn, ARTEMIS_QUEUE_INDEX_IN)
        logger.info(f"Подписка на очередь: {ARTEMIS_QUEUE_INDEX_IN}")

    def on_message(self, event):
        """
        Обрабатывает входящее сообщение из Artemis.

        Сообщение автоматически сопровождается информацией о том,
        из какой очереди оно пришло — event.link.source.address.

        Параметры
        ---------
        event : proton Event
            Содержит AMQP сообщение.
        """
        msg = event.message.body
        queue = event.link.source.address  # chat.in, email.in или index.in

        logger.info(f"Получено сообщение из {queue}: {msg}")

        # Обрабатываем в зависимости от типа очереди
        if queue in [ARTEMIS_QUEUE_CHAT_IN, ARTEMIS_QUEUE_EMAIL_IN]:
            # Для chat/email - отправляем в Redis
            route_message(queue, msg)
        elif queue == ARTEMIS_QUEUE_INDEX_IN:
            # Для index - отправляем в индексер
            route_index_message(msg)
        else:
            logger.warning(f"Неизвестная очередь: {queue}")


def start_consumer():
    """
    Запускает бесконечный цикл слушателя AMQP в отдельном потоке.
    """
    logger.info("Запуск Artemis consumer...")
    
    def run_consumer():
        Container(ArtemisConsumer()).run()
    
    thread = threading.Thread(target=run_consumer, daemon=True)
    thread.start()
    logger.info("Artemis consumer запущен в фоновом потоке")

