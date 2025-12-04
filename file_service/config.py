"""
Модуль конфигурации для file_service.

Определяет базовую директорию для хранимых файлов и настройки сервиса.
"""

import os

BASE_DIR = os.getenv("FILES_BASE_DIR", "/storage")
