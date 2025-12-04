"""
Функции для векторного поиска в OpenSearch.
"""

from opensearch_client import client
from config import INDEX_NAME
from logger import logger


def search_knn(vector: list, k: int = 1) -> dict:
    """
    Выполняет поиск ближайших соседей по вектору.

    Параметры
    ---------
    vector : list
        Вектор запроса.
    k : int
        Количество ближайших соседей.

    Returns
    -------
    dict
        _source найденного документа.
    """
    body = {
        "size": k,
        "query": {
            "knn": {
                "vector": {
                    "vector": vector,
                    "k": k,
                }
            }
        }
    }

    logger.info(f"Выполнение KNN-поиска по вектору: {vector}")
    resp = client.search(index=INDEX_NAME, body=body)
    return resp["hits"]["hits"][0]["_source"]

