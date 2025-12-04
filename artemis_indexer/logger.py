"""
Модуль настройки логирования.

Создаёт глобальный объект logger, используемый во всём сервисе.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("indexer_consumer")
