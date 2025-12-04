"""
Конфигурация сервиса rag_stub.

Содержит параметры подключения к Redis, OpenSearch и Artemis.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "docs")

QUEUE_CHATS = os.getenv("QUEUE_CHATS", "chats")
QUEUE_EMAIL = os.getenv("QUEUE_EMAIL", "email")

ARTEMIS_URL = os.getenv("ARTEMIS_URL", "amqp://artemis:artemis@artemis:61616")
CHAT_OUT_QUEUE = os.getenv("CHAT_OUT_QUEUE", "chat.out")
EMAIL_OUT_QUEUE = os.getenv("EMAIL_OUT_QUEUE", "email.out")

TASKIQ_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

