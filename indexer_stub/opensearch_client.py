from opensearchpy import OpenSearch
from config import OPENSEARCH_HOST, INDEX_NAME, VECTOR_DIM
from logger import logger

client = OpenSearch(
    hosts=[OPENSEARCH_HOST],
)

def ensure_index():
    """Создает индекс в OpenSearch, если он не существует."""
    try:
        exists = client.indices.exists(index=INDEX_NAME)
        if exists:
            logger.info(f"Индекс {INDEX_NAME} уже существует.")
            return
    except Exception as e:
        logger.warning(f"Ошибка при проверке существования индекса: {e}")

    body = {
        "settings": {
            "index": {"knn": True}
        },
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "chunk_id": {"type": "integer"},
                "content": {"type": "text"},
                "vector": {
                    "type": "knn_vector",
                    "dimension": VECTOR_DIM,
                    "method": {
                        "name": "hnsw",
                        "space_type": "l2",
                        "engine": "nmslib"
                    }
                }
            }
        }
    }

    logger.info(f"Создание индекса {INDEX_NAME} в OpenSearch...")
    try:
        client.indices.create(index=INDEX_NAME, body=body)
        logger.info(f"Индекс {INDEX_NAME} успешно создан.")
    except Exception as e:
        logger.error(f"Ошибка при создании индекса: {e}")
        raise
