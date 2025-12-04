"""
Точка входа translator_service — FastAPI приложение.
"""

from fastapi import FastAPI
from router import router
from logger import logger

app = FastAPI(title="Translator Service")

app.include_router(router)


@app.on_event("startup")
def startup():
    logger.info("translator_service запущен и готов принимать сообщения.")
