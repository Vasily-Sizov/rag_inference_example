"""
Реальная логика индексации файлов в OpenSearch.
"""
from config import CHUNK_SIZE, INDEX_NAME
from clients.file_service_internal import list_files, fetch_file
from clients.opensearch import client
from logger import logger
from embeddings_stub import generate_vector


def chunk_text(text: str, size: int) -> list[str]:
    """
    Разбивает текст на чанки заданного размера.
    
    Параметры
    ---------
    text : str
        Текст для разбиения.
    size : int
        Размер чанка.
    
    Возвращает
    ----------
    list[str]
        Список чанков текста.
    """
    return [text[i:i+size] for i in range(0, len(text), size)]


def index_all_files() -> int:
    """
    Индексирует все файлы из file_service в OpenSearch.
    
    Для каждого файла:
    1. Получает содержимое
    2. Разбивает на чанки
    3. Генерирует вектор для каждого чанка
    4. Сохраняет в OpenSearch
    
    Возвращает
    ----------
    int
        Общее количество проиндексированных чанков.
    """
    logger.info("Начало индексации файлов...")
    files = list_files()
    logger.info(f"Найдено файлов для индексации: {len(files)}")
    
    total = 0

    for file_name in files:
        try:
            text = fetch_file(file_name)
            chunks = chunk_text(text, CHUNK_SIZE)
            logger.info(f"Обработка файла {file_name}: {len(chunks)} чанков")

            for i, chunk in enumerate(chunks):
                vec = generate_vector()

                # Используем правильный API для OpenSearch
                document = {
                    "doc_id": file_name,
                    "chunk_id": i,
                    "content": chunk,
                    "vector": vec,
                }
                
                # В новых версиях opensearch-py используется document вместо body
                try:
                    client.index(
                        index=INDEX_NAME,
                        document=document
                    )
                except TypeError:
                    # Fallback для старых версий
                    client.index(
                        index=INDEX_NAME,
                        body=document
                    )

                total += 1

            logger.info(f"Проиндексировано {len(chunks)} чанков из файла {file_name}")
        except Exception as e:
            logger.error(f"Ошибка при индексации файла {file_name}: {e}")
            continue

    logger.info(f"Индексация завершена. Всего проиндексировано чанков: {total}")
    return total

