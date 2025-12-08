"""
Клиент OpenSearch для rag_service.

Используется для выполнения векторного поиска.
"""

from opensearchpy import OpenSearch
from config import OPENSEARCH_HOST
from logger import logger

logger.info(f"Подключение к OpenSearch: {OPENSEARCH_HOST}")

client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
)

