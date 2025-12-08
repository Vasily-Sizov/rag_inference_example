"""
Конфигурация сервиса rag_service.

Содержит параметры подключения к Redis, OpenSearch и translator_service.
"""

import os

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
INDEX_NAME = os.getenv("INDEX_NAME", "docs")

QUEUE_CHATS = os.getenv("QUEUE_CHATS", "chats")
QUEUE_EMAIL = os.getenv("QUEUE_EMAIL", "email")

# URL translator_service для отправки результатов
TRANSLATOR_SERVICE_URL = os.getenv(
    "TRANSLATOR_SERVICE_URL",
    "http://translator_service:8005/result/rag"
)

TASKIQ_BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"

