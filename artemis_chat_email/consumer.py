"""
AMQP-консьюмер, слушающий две очереди Artemis: chat.in и email.in.

При получении сообщения отправляет его в translator_service.
"""

from proton.handlers import MessagingHandler
from proton.reactor import Container
from config import ARTEMIS_URL, QUEUE_CHAT, QUEUE_EMAIL
from logger import logger
from http_client import send_to_translator


class ArtemisChatEmailConsumer(MessagingHandler):
    """
    Консьюмер Artemis, который слушает две очереди одновременно:
    chat.in и email.in.

    Каждый пришедший AMQP-месседж передаётся в translator_service.
    """

    def __init__(self):
        super().__init__()
        logger.info("Инициализация Artemis consumer для chat.in + email.in")

    def on_start(self, event):
        """
        Подключение к Artemis и создание двух подписчиков.
        """

        logger.info("Подключение к Artemis...")
        conn = event.container.connect(ARTEMIS_URL)

        # Подписка на chat.in
        event.container.create_receiver(conn, QUEUE_CHAT)
        logger.info(f"Подписка на очередь: {QUEUE_CHAT}")

        # Подписка на email.in
        event.container.create_receiver(conn, QUEUE_EMAIL)
        logger.info(f"Подписка на очередь: {QUEUE_EMAIL}")

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
        queue = event.link.source.address  # chat.in или email.in

        logger.info(f"Получено сообщение из {queue}: {msg}")

        # Формируем объект для translator_service
        payload = {
            "source_queue": queue,
            "body": msg,
        }

        send_to_translator(payload)


def start_consumer():
    """
    Запускает бесконечный цикл слушателя AMQP.
    """
    logger.info("Запуск сервиса artemis_chat_email...")
    Container(ArtemisChatEmailConsumer()).run()
