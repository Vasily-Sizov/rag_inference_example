"""
Конфигурационный модуль для сервиса artemis_chat_email.

Определяет параметры подключения к Artemis и адрес translator_service.
"""

import os

ARTEMIS_URL = os.getenv("ARTEMIS_URL", "amqp://artemis:artemis@artemis:61616")

QUEUE_CHAT = os.getenv("QUEUE_CHAT", "chat.in")
QUEUE_EMAIL = os.getenv("QUEUE_EMAIL", "email.in")

TRANSLATOR_URL = os.getenv("TRANSLATOR_URL", "http://translator_service:8005/ingest")
