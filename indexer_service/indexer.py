"""
Основная логика индексации, после завершения
отправляет результат в translator_service.
"""

import json
from logger import logger
from clients.translator_service_internal import send_result_to_translator
from indexer_service_module import index_all_files
from clients.opensearch import ensure_index


def run_indexing_pipeline():
    """
    Запускает реальную индексацию файлов и отправляет результат в translator_service.
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
    
    # Отправляем результат в translator_service
    body = json.dumps(result)
    send_result_to_translator(body)
    logger.info("Результат индексации отправлен в translator_service")

