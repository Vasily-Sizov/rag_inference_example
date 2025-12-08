"""
Конфигурационный модуль для translator_service.

Содержит параметры подключения к Redis, Artemis и имена очередей.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

QUEUE_CHATS = os.getenv("QUEUE_CHATS", "chats")
QUEUE_EMAIL = os.getenv("QUEUE_EMAIL", "email")

# Artemis настройки
ARTEMIS_URL = os.getenv("ARTEMIS_URL", "amqp://artemis:artemis@artemis:61616")
ARTEMIS_QUEUE_CHAT_IN = os.getenv("ARTEMIS_QUEUE_CHAT_IN", "chat.in")
ARTEMIS_QUEUE_EMAIL_IN = os.getenv("ARTEMIS_QUEUE_EMAIL_IN", "email.in")
ARTEMIS_QUEUE_INDEX_IN = os.getenv("ARTEMIS_QUEUE_INDEX_IN", "index.in")
ARTEMIS_QUEUE_CHAT_OUT = os.getenv("ARTEMIS_QUEUE_CHAT_OUT", "chat.out")
ARTEMIS_QUEUE_EMAIL_OUT = os.getenv("ARTEMIS_QUEUE_EMAIL_OUT", "email.out")
ARTEMIS_QUEUE_INDEX_OUT = os.getenv("ARTEMIS_QUEUE_INDEX_OUT", "index.out")

# Indexer настройки
INDEXER_URL = os.getenv("INDEXER_URL", "http://indexer_service:8001/index")
