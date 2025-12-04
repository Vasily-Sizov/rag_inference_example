"""
Модуль конфигурации для indexer_consumer.

Определяет параметры подключения к Artemis и адрес сервиса indexer_stub.
"""

import os

ARTEMIS_URL = os.getenv("ARTEMIS_URL", "amqp://artemis:artemis@artemis:61616")
INDEXER_URL = os.getenv("INDEXER_URL", "http://indexer_stub:8001/index")
QUEUE_NAME = os.getenv("QUEUE_NAME", "index.in")
