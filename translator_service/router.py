"""
HTTP-маршруты сервиса translator_service.

Принимает входящие сообщения от artemis_chat_email
и перенаправляет их в очередь Redis.
"""

from fastapi import APIRouter
from logic import route_message

router = APIRouter()


@router.post("/ingest")
def ingest_message(payload: dict):
    """
    Принимает сообщение от артемис-консьюмера и отправляет его в Redis.

    Параметры
    ---------
    payload : dict
        Формат:
        {
            "source_queue": "chat.in" или "email.in",
            "body": "текст сообщения"
        }

    Возвращает
    ----------
    dict
        Информация о том, в какую очередь Redis отправлен месседж.
    """

    source = payload["source_queue"]
    body = payload["body"]

    redis_dest = route_message(source, body)

    return {
        "status": "ok",
        "redis_queue": redis_dest
    }
