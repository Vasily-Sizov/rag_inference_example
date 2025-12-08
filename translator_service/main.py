"""
Точка входа translator_service — FastAPI приложение с AMQP консьюмером.
"""

from fastapi import FastAPI
from router import router
from logger import logger
from clients.artemis_consumer import start_consumer

app = FastAPI(title="Translator Service")

app.include_router(router)


@app.on_event("startup")
def startup():
    logger.info("translator_service запущен и готов принимать сообщения.")
    # Запускаем AMQP консьюмер в фоновом потоке
    start_consumer()
