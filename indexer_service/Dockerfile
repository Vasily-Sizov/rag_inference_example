FROM python:3.11-slim

# Рабочая директория контейнера
WORKDIR /app

# Устанавливаем зависимости системы (иногда нужны для OpenSearch)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем проект
COPY . .

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    requests \
    opensearch-py \
    numpy

# Команда запуска сервиса
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

