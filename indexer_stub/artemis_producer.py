from proton import Message
from proton.reactor import Container
from config import ARTEMIS_URL, OUT_QUEUE_NAME
from logger import logger

class _OneShotSender:
    """Одноразовая отправка сообщения в Artemis."""

    def __init__(self, queue: str, body: str):
        self.queue = queue
        self.body = body

    def on_start(self, event):
        conn = event.container.connect(ARTEMIS_URL)
        sender = event.container.create_sender(conn, self.queue)
        logger.info(f"Отправка в {self.queue}: {self.body}")
        sender.send(Message(body=self.body))
        conn.close()
        event.container.stop()


def send_to_artemis(queue: str, body: str):
    Container(_OneShotSender(queue, body)).run()
