"""
HTTP-маршруты сервиса translator_service.

Принимает входящие сообщения и результаты от других сервисов.
"""

import json
from fastapi import APIRouter
from logic import route_message, route_index_message
from clients.artemis_producer import send_to_artemis
from config import (
    ARTEMIS_QUEUE_CHAT_OUT,
    ARTEMIS_QUEUE_EMAIL_OUT,
    ARTEMIS_QUEUE_INDEX_OUT,
)
from logger import logger

router = APIRouter()


@router.post("/ingest")
def ingest_message(payload: dict):
    """
    Принимает сообщение от артемис-консьюмера и отправляет его в Redis.
    (Оставлено для обратной совместимости, но теперь консьюмер работает напрямую)

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


@router.post("/chat")
def process_chat_direct(payload: dict):
    """
    Прямой запрос на обработку чата (обходя Artemis).

    Параметры
    ---------
    payload : dict
        Формат:
        {
            "body": "текст сообщения"
        }

    Возвращает
    ----------
    dict
        Статус обработки.
    """
    body = payload.get("body", "")
    logger.info(f"Прямой запрос на обработку чата: {body}")
    
    route_message("chat.in", body)
    
    return {
        "status": "ok",
        "message": "Сообщение отправлено в Redis очередь для обработки"
    }


@router.post("/email")
def process_email_direct(payload: dict):
    """
    Прямой запрос на обработку email (обходя Artemis).

    Параметры
    ---------
    payload : dict
        Формат:
        {
            "body": "текст сообщения"
        }

    Возвращает
    ----------
    dict
        Статус обработки.
    """
    body = payload.get("body", "")
    logger.info(f"Прямой запрос на обработку email: {body}")
    
    route_message("email.in", body)
    
    return {
        "status": "ok",
        "message": "Сообщение отправлено в Redis очередь для обработки"
    }


@router.post("/index")
def process_index_direct(payload: dict = None):
    """
    Прямой запрос на индексацию (обходя Artemis).

    Параметры
    ---------
    payload : dict, optional
        Может содержать параметры индексации.

    Возвращает
    ----------
    dict
        Статус обработки.
    """
    body = ""
    if payload:
        body = json.dumps(payload)
    
    logger.info(f"Прямой запрос на индексацию: {body}")
    
    route_index_message(body)
    
    return {
        "status": "ok",
        "message": "Индексация запущена"
    }


@router.post("/result/rag")
def receive_rag_result(payload: dict):
    """
    Принимает результат от rag_service и отправляет его в Artemis.

    Параметры
    ---------
    payload : dict
        Формат:
        {
            "source_queue": "chats" или "email",
            "result": "текст результата"
        }

    Возвращает
    ----------
    dict
        Статус обработки.
    """
    source_queue = payload.get("source_queue", "")
    result = payload.get("result", "")
    
    logger.info(f"Получен результат от rag_service из очереди {source_queue}: {result}")
    
    # Определяем целевую очередь Artemis
    if source_queue == "chats":
        out_queue = ARTEMIS_QUEUE_CHAT_OUT
    elif source_queue == "email":
        out_queue = ARTEMIS_QUEUE_EMAIL_OUT
    else:
        logger.warning(f"Неизвестная очередь-источник: {source_queue}")
        return {
            "status": "error",
            "message": f"Неизвестная очередь-источник: {source_queue}"
        }
    
    # Отправляем в Artemis
    send_to_artemis(out_queue, result)
    
    return {
        "status": "ok",
        "message": f"Результат отправлен в {out_queue}"
    }


@router.post("/result/indexer")
def receive_indexer_result(payload: dict):
    """
    Принимает результат от indexer_service и отправляет его в Artemis.

    Параметры
    ---------
    payload : dict
        Формат:
        {
            "result": "JSON строка с результатом индексации"
        }

    Возвращает
    ----------
    dict
        Статус обработки.
    """
    result = payload.get("result", "")
    
    logger.info(f"Получен результат от indexer_service: {result}")
    
    # Отправляем в Artemis
    send_to_artemis(ARTEMIS_QUEUE_INDEX_OUT, result)
    
    return {
        "status": "ok",
        "message": f"Результат отправлен в {ARTEMIS_QUEUE_INDEX_OUT}"
    }
