"""
AMQP-консьюмер, который слушает очередь Artemis и реагирует на сообщения.

Когда приходит новое сообщение в очередь index.in — запускается индексация.
"""

from proton.handlers import MessagingHandler
from proton.reactor import Container
from logger import logger
from http_client import trigger_indexing
from config import ARTEMIS_URL, QUEUE_NAME


class IndexerConsumer(MessagingHandler):
    """
    Класс-консьюмер для Artemis.

    Слушает очередь index.in. При получении сообщения запускает процедуру
    индексации через вызов HTTP-метода на indexer_stub.
    """

    def __init__(self):
        super().__init__()
        logger.info(f"Инициализация слушателя очереди: {QUEUE_NAME}")

    def on_start(self, event):
        """
        Вызывается при старте консьюмера. Устанавливает соединение и
        подписку на очередь Artemis.
        """
        logger.info("Подключение к Artemis...")
        conn = event.container.connect(ARTEMIS_URL)
        event.container.create_receiver(conn, QUEUE_NAME)
        logger.info(f"Подписка на очередь Artemis: {QUEUE_NAME}")

    def on_message(self, event):
        """
        Обрабатывает входящее сообщение из очереди Artemis.

        Parameters
        ----------
        event : proton Event
            Содержит сообщение AMQP.

        Notes
        -----
        В самом сообщении может быть payload, например {"force": true},
        но в базовом варианте мы его не используем. Любое сообщение
        означает “запустить индексацию”.
        """
        logger.info(f"Получено сообщение из {QUEUE_NAME}: {event.message.body}")

        # Запускаем индексацию
        trigger_indexing()


def start_consumer():
    """
    Запускает бесконечный цикл обработки сообщений Artemis.
    """
    logger.info("Запуск AMQP-консьюмера index.in...")
    Container(IndexerConsumer()).run()
