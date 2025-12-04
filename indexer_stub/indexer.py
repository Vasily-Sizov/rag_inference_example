"""
Основная логика индексации, после завершения
отправляет результат в index.out в Artemis.
"""

import json
from logger import logger
from config import OUT_QUEUE_NAME
from artemis_producer import send_to_artemis
from indexer_service import index_all_files
from opensearch_client import ensure_index


def run_indexing_pipeline():
    """
    Запускает реальную индексацию файлов и отправляет результат в Artemis.
    """
    logger.info("Запуск pipeline индексации...")
    
    # Убеждаемся, что индекс создан
    ensure_index()
    
    # Запускаем индексацию
    try:
        total = index_all_files()
        result = {"status": "ok", "count": total}
        logger.info(f"Индексация завершена успешно: создано {total} чанков.")
    except Exception as e:
        logger.error(f"Ошибка при индексации: {e}", exc_info=True)
        result = {"status": "error", "message": str(e), "count": 0}
    
    # Отправляем результат в Artemis
    body = json.dumps(result)
    send_to_artemis(OUT_QUEUE_NAME, body)
    logger.info(f"Результат индексации отправлен в очередь {OUT_QUEUE_NAME}")
