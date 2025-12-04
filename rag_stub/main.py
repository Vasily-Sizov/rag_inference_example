"""
FastAPI-приложение rag_stub (health-check).

Вся основная работа происходит в worker.py, но API можно использовать
для проверки статуса.
"""

from fastapi import FastAPI
from logger import logger

app = FastAPI(title="RAG Stub")


@app.on_event("startup")
async def startup():
    logger.info("RAG stub API запущен.")


@app.get("/health")
def health():
    """
    Возвращает статус сервиса.

    Returns
    -------
    dict
        {"status": "ok"}
    """
    return {"status": "ok"}

