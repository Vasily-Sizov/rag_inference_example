"""
Конфигурация логирования для file_service.

Определяет глобальный экземпляр логгера с единым форматом сообщений.
"""

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger("file_service")
