import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL", "http://file_service:9001")
INDEX_NAME = os.getenv("INDEX_NAME", "docs")
VECTOR_DIM = 10
CHUNK_SIZE = 50

# URL translator_service для отправки результатов
TRANSLATOR_SERVICE_URL = os.getenv(
    "TRANSLATOR_SERVICE_URL",
    "http://translator_service:8005/result/indexer"
)

