#!/bin/bash
# Скрипт для запуска тестов через uv

echo "Проверка установки uv..."
if ! command -v uv &> /dev/null; then
    echo "uv не установлен. Устанавливаю..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    if [ $? -ne 0 ]; then
        echo "Ошибка установки uv. Установите вручную: https://github.com/astral-sh/uv"
        exit 1
    fi
fi

echo "Синхронизация зависимостей..."
uv sync --no-install-project

echo "Запуск тестов..."
uv run python test_pipeline.py "$@"

