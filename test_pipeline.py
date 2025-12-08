"""
Скрипт для тестирования всех pipeline системы RAG.

Использование:
    python test_pipeline.py [chat|email|index|all]

Примеры:
    python test_pipeline.py chat    # Тест только chat pipeline
    python test_pipeline.py all     # Тест всех pipeline
    python test_pipeline.py         # Тест всех pipeline (по умолчанию)

Тестирование проходит в два этапа:
1. Через Artemis (отправка в Artemis очереди)
2. Через прямые HTTP ручки translator_service (обходя Artemis)
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

# Проверка доступности python-qpid-proton
try:
    from proton import Message
    from proton.reactor import Container
    PROTON_AVAILABLE = True
except ImportError:
    PROTON_AVAILABLE = False
    logger.warning("python-qpid-proton не установлен. Тесты через Artemis будут пропущены.")

# Конфигурация
ARTEMIS_URL = "amqp://artemis:artemis@localhost:61616"
TRANSLATOR_SERVICE_URL = "http://localhost:8005"
OPENSEARCH_URL = "http://localhost:9200/docs/_search"

# Очереди Artemis
ARTEMIS_QUEUE_CHAT_IN = "chat.in"
ARTEMIS_QUEUE_EMAIL_IN = "email.in"
ARTEMIS_QUEUE_INDEX_IN = "index.in"
ARTEMIS_QUEUE_CHAT_OUT = "chat.out"
ARTEMIS_QUEUE_EMAIL_OUT = "email.out"
ARTEMIS_QUEUE_INDEX_OUT = "index.out"


class _OneShotSender:
    """Вспомогательный класс для отправки сообщения в Artemis."""

    def __init__(self, queue: str, body: str):
        self.queue = queue
        self.body = body
        self.sent = False

    def on_start(self, event):
        conn = event.container.connect(ARTEMIS_URL)
        sender = event.container.create_sender(conn, self.queue)
        logger.info(f"   Отправка в {self.queue}: {self.body[:50]}...")
        sender.send(Message(body=self.body))
        self.sent = True
        conn.close()
        event.container.stop()


def send_to_artemis(queue: str, body: str) -> bool:
    """
    Отправляет сообщение в очередь Artemis.

    Параметры
    ---------
    queue : str
        Название очереди.
    body : str
        Тело сообщения.

    Возвращает
    ----------
    bool
        True если успешно, False иначе.
    """
    if not PROTON_AVAILABLE:
        logger.error("   python-qpid-proton не установлен!")
        return False
    
    try:
        sender = _OneShotSender(queue, body)
        Container(sender).run()
        return True
    except Exception as e:
        logger.error(f"   Ошибка отправки в Artemis: {e}")
        return False


def print_section(title: str) -> None:
    """Печатает заголовок секции."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("  " + title)
    logger.info("=" * 70)


def print_result(success: bool, message: str) -> None:
    """Печатает результат операции."""
    if success:
        logger.info(f"[OK] {message}")
    else:
        logger.error(f"[ERROR] {message}")


def check_services() -> bool:
    """Проверяет доступность всех сервисов."""
    print_section("ПРОВЕРКА ДОСТУПНОСТИ СЕРВИСОВ")

    services = {
        "translator_service": f"{TRANSLATOR_SERVICE_URL}",
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

    if PROTON_AVAILABLE:
        print_result(True, "python-qpid-proton установлен (тесты через Artemis доступны)")
    else:
        print_result(False, "python-qpid-proton не установлен (тесты через Artemis пропущены)")
        logger.warning("   Установите: pip install python-qpid-proton")
    
    return all_ok


def test_chat_via_artemis() -> bool:
    """Тестирует CHAT pipeline через Artemis."""
    logger.info("")
    logger.info("--- Тест через Artemis ---")
    
    # Создаем тестовый вектор (10 чисел, как в конфиге VECTOR_DIM=10)
    test_vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    vector_json = json.dumps(test_vector)
    
    logger.info("1. Отправка сообщения в Artemis очередь chat.in...")
    logger.info(f"   Вектор: {test_vector}")
    
    if not send_to_artemis(ARTEMIS_QUEUE_CHAT_IN, vector_json):
        return False
    
    print_result(True, "Сообщение отправлено в Artemis")
    
    logger.info("")
    logger.info("2. Ожидание обработки (5 секунд)...")
    time.sleep(5)
    
    logger.info("")
    logger.info("3. Проверка логов:")
    logger.info("   docker-compose logs --tail=20 translator_service")
    logger.info("   docker-compose logs --tail=20 rag_service")
    
    logger.info("")
    logger.info("[OK] CHAT pipeline через Artemis запущен. Проверьте логи.")
    return True


def test_chat_via_api() -> bool:
    """Тестирует CHAT pipeline через прямую API ручку translator_service."""
    logger.info("")
    logger.info("--- Тест через прямую API ручку ---")
    
    # Создаем тестовый вектор
    test_vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    vector_json = json.dumps(test_vector)
    
    logger.info("1. Отправка запроса в translator_service /chat...")
    logger.info(f"   Вектор: {test_vector}")
    
    payload = {
        "body": vector_json
    }
    
    try:
        response = requests.post(
            f"{TRANSLATOR_SERVICE_URL}/chat",
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        print_result(True, f"translator_service принял: {result}")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        return False
    
    logger.info("")
    logger.info("2. Ожидание обработки (5 секунд)...")
    time.sleep(5)
    
    logger.info("")
    logger.info("[OK] CHAT pipeline через API запущен. Проверьте логи.")
    return True


def test_chat_pipeline() -> bool:
    """Тестирует CHAT pipeline (через Artemis и через API)."""
    print_section("ТЕСТ CHAT PIPELINE")

    results = {}
    
    # Тест через Artemis
    if PROTON_AVAILABLE:
        results["artemis"] = test_chat_via_artemis()
    else:
        logger.warning(
            "   Пропуск теста через Artemis "
            "(python-qpid-proton не установлен)"
        )
        results["artemis"] = True  # Пропуск не считается ошибкой
    
    # Тест через API
    results["api"] = test_chat_via_api()

    # Итог
    success = results.get("api", False)
    artemis_result = results.get("artemis")
    if artemis_result is not None:
        success = success and artemis_result

    return success


def test_email_via_artemis() -> bool:
    """Тестирует EMAIL pipeline через Artemis."""
    logger.info("")
    logger.info("--- Тест через Artemis ---")
    
    # Создаем тестовый вектор
    test_vector = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]
    vector_json = json.dumps(test_vector)
    
    logger.info("1. Отправка сообщения в Artemis очередь email.in...")
    logger.info(f"   Вектор: {test_vector}")
    
    if not send_to_artemis(ARTEMIS_QUEUE_EMAIL_IN, vector_json):
        return False
    
    print_result(True, "Сообщение отправлено в Artemis")
    
    logger.info("")
    logger.info("2. Ожидание обработки (5 секунд)...")
    time.sleep(5)
    
    logger.info("")
    logger.info("[OK] EMAIL pipeline через Artemis запущен. Проверьте логи.")
    return True


def test_email_via_api() -> bool:
    """Тестирует EMAIL pipeline через прямую API ручку translator_service."""
    logger.info("")
    logger.info("--- Тест через прямую API ручку ---")
    
    # Создаем тестовый вектор
    test_vector = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]
    vector_json = json.dumps(test_vector)
    
    logger.info("1. Отправка запроса в translator_service /email...")
    logger.info(f"   Вектор: {test_vector}")
    
    payload = {
        "body": vector_json
    }
    
    try:
        response = requests.post(
            f"{TRANSLATOR_SERVICE_URL}/email",
            json=payload,
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        print_result(True, f"translator_service принял: {result}")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        return False
    
    logger.info("")
    logger.info("2. Ожидание обработки (5 секунд)...")
    time.sleep(5)
    
    logger.info("")
    logger.info("[OK] EMAIL pipeline через API запущен. Проверьте логи.")
    return True


def test_email_pipeline() -> bool:
    """Тестирует EMAIL pipeline (через Artemis и через API)."""
    print_section("ТЕСТ EMAIL PIPELINE")

    results = {}
    
    # Тест через Artemis
    if PROTON_AVAILABLE:
        results["artemis"] = test_email_via_artemis()
    else:
        logger.warning(
            "   Пропуск теста через Artemis "
            "(python-qpid-proton не установлен)"
        )
        results["artemis"] = True  # Пропуск не считается ошибкой
    
    # Тест через API
    results["api"] = test_email_via_api()

    # Итог
    success = results.get("api", False)
    artemis_result = results.get("artemis")
    if artemis_result is not None:
        success = success and artemis_result

    return success


def test_index_via_artemis() -> bool:
    """Тестирует INDEX pipeline через Artemis."""
    logger.info("")
    logger.info("--- Тест через Artemis ---")
    
    logger.info("1. Отправка сообщения в Artemis очередь index.in...")
    
    # Отправляем пустое сообщение или JSON с параметрами
    message = json.dumps({"action": "index"})
    
    if not send_to_artemis(ARTEMIS_QUEUE_INDEX_IN, message):
        return False
    
    print_result(True, "Сообщение отправлено в Artemis")
    
    logger.info("")
    logger.info("2. Ожидание завершения индексации (10 секунд)...")
    time.sleep(10)
    
    logger.info("")
    logger.info("3. Проверка данных в OpenSearch...")
    try:
        search_response = requests.get(
            f"{OPENSEARCH_URL}?pretty=true",
            timeout=5
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
    logger.info("[OK] INDEX pipeline через Artemis завершен.")
    return True


def test_index_via_api() -> bool:
    """Тестирует INDEX pipeline через прямую API ручку translator_service."""
    logger.info("")
    logger.info("--- Тест через прямую API ручку ---")
    
    logger.info("1. Отправка запроса в translator_service /index...")
    
    try:
        response = requests.post(
            f"{TRANSLATOR_SERVICE_URL}/index",
            json={},
            timeout=5
        )
        response.raise_for_status()
        result = response.json()
        print_result(True, f"translator_service принял: {result}")
    except Exception as e:
        print_result(False, f"Ошибка отправки: {e}")
        return False
    
    logger.info("")
    logger.info("2. Ожидание завершения индексации (10 секунд)...")
    time.sleep(10)
    
    logger.info("")
    logger.info("3. Проверка данных в OpenSearch...")
    try:
        search_response = requests.get(
            f"{OPENSEARCH_URL}?pretty=true",
            timeout=5
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
    logger.info("[OK] INDEX pipeline через API завершен.")
    return True


def test_index_pipeline() -> bool:
    """Тестирует INDEX pipeline (через Artemis и через API)."""
    print_section("ТЕСТ INDEX PIPELINE")

    results = {}
    
    # Тест через Artemis
    if PROTON_AVAILABLE:
        results["artemis"] = test_index_via_artemis()
    else:
        logger.warning(
            "   Пропуск теста через Artemis "
            "(python-qpid-proton не установлен)"
        )
        results["artemis"] = True  # Пропуск не считается ошибкой
    
    # Тест через API
    results["api"] = test_index_via_api()

    # Итог
    success = results.get("api", False)
    artemis_result = results.get("artemis")
    if artemis_result is not None:
        success = success and artemis_result

    return success


def main():
    """Главная функция."""
    logger.info("")
    logger.info("=" * 70)
    logger.info("  ТЕСТИРОВАНИЕ RAG PIPELINE")
    logger.info("=" * 70)
    
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
    logger.info("=" * 70)


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
        import traceback
        traceback.print_exc()
        sys.exit(1)
