"""
Скрипт для тестирования всех pipeline системы RAG.

Использование:
    python test_pipeline.py [chat|email|index|all]

Примеры:
    python test_pipeline.py chat    # Тест только chat pipeline
    python test_pipeline.py all     # Тест всех pipeline
    python test_pipeline.py         # Тест всех pipeline (по умолчанию)
"""

import requests
import json
import time
import sys
import logging


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Конфигурация
TRANSLATOR_URL = "http://localhost:8005/ingest"
INDEXER_URL = "http://localhost:8001/index"
OPENSEARCH_URL = "http://localhost:9200/docs/_search"


def print_section(title: str) -> None:
    """Печатает заголовок секции."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("  " + title)
    logger.info("=" * 60)


def print_result(success: bool, message: str) -> None:
    """Печатает результат операции."""
    if success:
        logger.info(f"[OK] УСПЕХ: {message}")
    else:
        logger.error(f"[ERROR] ОШИБКА: {message}")


def test_chat_pipeline() -> bool:
    """Тестирует CHAT pipeline."""
    print_section("ТЕСТ CHAT PIPELINE")

    # Создаем тестовый вектор (10 чисел, как в конфиге VECTOR_DIM=10)
    test_vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    vector_json = json.dumps(test_vector)

    logger.info("1. Отправка сообщения в translator_service...")
    logger.info(f"   Вектор: {test_vector}")

    payload = {
        "source_queue": "chat.in",
        "body": vector_json
    }

    try:
        response = requests.post(TRANSLATOR_URL, json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        print_result(True, f"translator_service принял: {result}")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        return False

    logger.info("")
    logger.info("2. Ожидание обработки (3 секунды)...")
    time.sleep(3)

    logger.info("")
    logger.info("3. Проверка логов:")
    logger.info("   docker-compose logs --tail=20 rag_stub")
    logger.info("   docker-compose logs --tail=10 translator_service")

    logger.info("")
    logger.info("[OK] CHAT pipeline запущен. Проверьте логи.")
    return True


def test_email_pipeline() -> bool:
    """Тестирует EMAIL pipeline."""
    print_section("ТЕСТ EMAIL PIPELINE")

    # Создаем тестовый вектор
    test_vector = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]
    vector_json = json.dumps(test_vector)

    logger.info("1. Отправка сообщения в translator_service...")
    logger.info(f"   Вектор: {test_vector}")

    payload = {
        "source_queue": "email.in",
        "body": vector_json
    }

    try:
        response = requests.post(TRANSLATOR_URL, json=payload, timeout=5)
        response.raise_for_status()
        result = response.json()
        print_result(True, f"translator_service принял: {result}")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        return False

    logger.info("")
    logger.info("2. Ожидание обработки (3 секунды)...")
    time.sleep(3)

    logger.info("")
    logger.info("[OK] EMAIL pipeline запущен. Проверьте логи.")
    return True


def test_index_pipeline() -> bool:
    """Тестирует INDEX pipeline."""
    print_section("ТЕСТ INDEX PIPELINE")

    logger.info("1. Отправка запроса на индексацию в indexer_stub...")

    try:
        response = requests.post(INDEXER_URL, timeout=30)
        response.raise_for_status()
        result = response.json()
        print_result(True, f"indexer_stub принял запрос: {result}")
    except Exception as e:
        print_result(False, f"Ошибка при отправке в indexer_stub: {e}")
        return False

    logger.info("")
    logger.info("2. Ожидание завершения индексации (5 секунд)...")
    time.sleep(5)

    logger.info("")
    logger.info("3. Проверка данных в OpenSearch...")
    try:
        search_response = requests.get(
            f"{OPENSEARCH_URL}?pretty=true", timeout=5
        )
        search_response.raise_for_status()
        data = search_response.json()
        total = data.get("hits", {}).get("total", {}).get("value", 0)
        print_result(True, f"В OpenSearch найдено документов: {total}")

        if total > 0:
            logger.info("")
            logger.info("   Примеры документов:")
            for hit in data.get("hits", {}).get("hits", [])[:3]:
                source = hit.get("_source", {})
                doc_id = source.get('doc_id')
                chunk_id = source.get('chunk_id')
                content = source.get('content', '')[:50]
                msg = (f"   - doc_id: {doc_id}, "
                       f"chunk_id: {chunk_id}, "
                       f"content: {content}...")
                logger.info(msg)
    except Exception as e:
        print_result(False, f"Ошибка проверки OpenSearch: {e}")

    logger.info("")
    logger.info("4. Проверка логов:")
    logger.info("   docker-compose logs --tail=30 indexer_stub")

    logger.info("")
    logger.info("[OK] INDEX pipeline завершен.")
    return True


def check_services() -> bool:
    """Проверяет доступность всех сервисов."""
    print_section("ПРОВЕРКА ДОСТУПНОСТИ СЕРВИСОВ")

    services = {
        "translator_service": "http://localhost:8005",
        "indexer_stub": "http://localhost:8001",
        "file_service": "http://localhost:9001",
        "opensearch": "http://localhost:9200",
    }

    all_ok = True
    for name, url in services.items():
        try:
            requests.get(url, timeout=2)
            print_result(True, f"{name} доступен ({url})")
        except Exception as e:
            print_result(False, f"{name} недоступен ({url}): {e}")
            all_ok = False

    return all_ok


def main():
    """Главная функция."""
    logger.info("")
    logger.info("=" * 60)
    logger.info("  ТЕСТИРОВАНИЕ RAG PIPELINE")
    logger.info("=" * 60)

    # Проверяем доступность сервисов
    if not check_services():
        logger.warning("")
        logger.warning("[WARNING] ВНИМАНИЕ: Некоторые сервисы недоступны!")
        logger.warning("   Убедитесь, что все контейнеры запущены:")
        logger.warning("   docker-compose ps")
        response = input("\n   Продолжить тестирование? (y/n): ")
        if response.lower() != 'y':
            return

    # Определяем, какие тесты запускать
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
    else:
        test_type = "all"

    results = {}

    if test_type in ["chat", "all"]:
        results["chat"] = test_chat_pipeline()

    if test_type in ["email", "all"]:
        results["email"] = test_email_pipeline()

    if test_type in ["index", "all"]:
        results["index"] = test_index_pipeline()

    # Итоги
    print_section("ИТОГИ ТЕСТИРОВАНИЯ")

    for test_name, success in results.items():
        status = "[OK] ПРОЙДЕН" if success else "[FAIL] ПРОВАЛЕН"
        logger.info(f"{test_name.upper()}: {status}")

    all_passed = all(results.values())
    if all_passed:
        logger.info("")
        logger.info("[OK] Все тесты пройдены успешно!")
    else:
        msg = "Некоторые тесты провалились. Проверьте логи."
        logger.warning("")
        logger.warning(f"[WARNING] {msg}")

    logger.info("")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("")
        logger.info("")
        logger.warning("Тестирование прервано пользователем.")
        sys.exit(1)
    except Exception as e:
        logger.error("")
        logger.error("")
        logger.error(f"Критическая ошибка: {e}")
        sys.exit(1)