"""
Конфигурационный модуль для translator_service.

Содержит параметры подключения к Redis и имена очередей.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

QUEUE_CHATS = os.getenv("QUEUE_CHATS", "chats")
QUEUE_EMAIL = os.getenv("QUEUE_EMAIL", "email")
