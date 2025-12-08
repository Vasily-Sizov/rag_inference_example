# RAG Infrastructure Test Stand

> **Важно**: Это тестовая инфраструктура для проверки работы распределенной архитектуры с очередями сообщений, векторным поиском и асинхронной обработкой запросов. Не предназначена для продакшн-использования.

## Описание

Тестовый стенд для проверки работы распределенной RAG-подобной архитектуры. Система использует заглушки для генерации векторов.

**Основная цель**: Проверка корректной работы инфраструктуры:
- Очереди сообщений (Artemis, Redis)
- Векторная база данных (OpenSearch)
- Микросервисная архитектура
- Асинхронная обработка запросов
- Индексация документов

## Архитектура

Система состоит из 7 сервисов, работающих в Docker-контейнерах:

**Инфраструктура:**
- `artemis` - брокер сообщений (AMQP)
- `redis` - очереди для асинхронной обработки
- `opensearch` - векторная база данных

**Сервисы приложения:**
- `file_service` - HTTP-сервис для работы с файлами
- `translator_service` - сервис-переходник (слушает Artemis, маршрутизирует сообщения)
- `rag_service` - воркер для обработки RAG-запросов
- `indexer_service` - сервис индексации документов

Подробное описание архитектуры: [architecture.md](architecture.md)

## Быстрый старт

```bash
# 1. Запуск всех сервисов
docker compose up --build

# 2. Дождитесь запуска (30-60 секунд)
docker compose ps

# 3. Запуск тестов
uv run python test_pipeline.py

# Или через скрипт
./run_tests.sh
```

## Pipeline

Система поддерживает 3 основных pipeline:

1. **INDEX** - индексация документов из `/storage` в OpenSearch
2. **CHAT** - обработка запросов из чата (вектор → поиск → ответ)
3. **EMAIL** - обработка запросов из email (вектор → поиск → ответ)

Все pipeline могут работать через Artemis (асинхронно) или через прямые HTTP API ручки `translator_service` (синхронно).

## Документация

- [architecture.md](architecture.md) - описание архитектуры, сервисов и потоков данных
- [manual_test.md](manual_test.md) - инструкции по ручному тестированию

## Мониторинг

**Artemis (веб-консоль):**
- URL: http://localhost:8161
- Логин/Пароль: `artemis` / `artemis`

**OpenSearch:**
- URL: http://localhost:9200
- Поиск: http://localhost:9200/docs/_search?pretty=true

**Redis:**
```bash
docker compose exec redis redis-cli
LLEN chats  # Проверка очереди
```

## Технологии

- Python 3.11
- FastAPI - REST API сервисы
- Apache ActiveMQ Artemis - брокер сообщений (AMQP)
- Redis - очереди для асинхронной обработки
- OpenSearch - векторный поиск (KNN)
- Docker Compose - оркестрация сервисов
- uv - управление зависимостями для тестов

## Ограничения

- Векторы генерируются заглушкой (`embeddings_stub`) - случайные числа
- Не предназначено для продакшн-использования
- Тестовая система для проверки инфраструктуры
- Минимальная обработка ошибок

## Тестирование

```bash
# Установка зависимостей (первый раз)
uv sync --no-install-project

# Все pipeline
uv run python test_pipeline.py

# Отдельные pipeline
uv run python test_pipeline.py index
uv run python test_pipeline.py chat
uv run python test_pipeline.py email
```

## Структура проекта

```
rag_stend/
├── file_service/          # HTTP-сервис файлов
├── indexer_service/      # Индексация документов
├── rag_service/           # RAG-воркер
├── translator_service/   # Сервис-переходник
├── storage/              # Файлы для индексации
├── docker-compose.yml    # Конфигурация сервисов
├── architecture.md       # Архитектура системы
├── manual_test.md        # Инструкции по тестированию
├── test_pipeline.py      # Автоматические тесты
├── pyproject.toml        # Зависимости для тестов
└── run_tests.sh          # Скрипт запуска тестов
```

## Разработка

**Пересборка сервиса:**
```bash
docker compose build <service_name>
docker compose up -d <service_name>
```

**Просмотр логов:**
```bash
docker compose logs -f <service_name>
```

**Остановка:**
```bash
docker compose down
```

## Примечания

- Все векторы имеют размерность 10 (VECTOR_DIM=10)
- Чанки документов разбиваются по 50 символов (CHUNK_SIZE=50)
- Индекс в OpenSearch называется `docs`
- Все сервисы работают в единой Docker-сети
- Для тестов используется `uv` - зависимости в `pyproject.toml`
