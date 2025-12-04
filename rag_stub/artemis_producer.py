"""
Отправка ответов из rag_stub в Artemis OUT-очереди.
"""

from proton import Message
from proton.reactor import Container
from config import ARTEMIS_URL
from logger import logger


class _OneShotSender:
    """
    Вспомогательный класс для одноразовой отправки сообщения
    в указанную очередь Artemis.
    """

    def __init__(self, queue: str, body: str):
        self.queue = queue
        self.body = body
        self.sent = False

    def on_start(self, event):
        """
        Устанавливает соединение и создаёт sender.
        """
        conn = event.container.connect(ARTEMIS_URL)
        sender = event.container.create_sender(conn, self.queue)
        logger.info(f"Отправка сообщения в Artemis очередь {self.queue}: {self.body}")
        sender.send(Message(body=self.body))
        self.sent = True
        conn.close()
        event.container.stop()


def send_to_artemis(queue: str, body: str):
    """
    Отправляет одно сообщение в указанную очередь Artemis.

    Параметры
    ---------
    queue : str
        Название очереди в Artemis (например, chat.out или email.out).
    body : str
        Тело сообщения.
    """
    sender = _OneShotSender(queue, body)
    Container(sender).run()
