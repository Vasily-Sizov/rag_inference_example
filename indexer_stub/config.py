import os

OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "http://opensearch:9200")
FILE_SERVICE_URL = os.getenv("FILE_SERVICE_URL", "http://file_service:9001")
INDEX_NAME = os.getenv("INDEX_NAME", "docs")
VECTOR_DIM = 10
CHUNK_SIZE = 50
ARTEMIS_URL = os.getenv("ARTEMIS_URL", "amqp://artemis:artemis@artemis:61616")
OUT_QUEUE_NAME = os.getenv("OUT_QUEUE_NAME", "index.out")
