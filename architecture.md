# Архитектура системы RAG

## Обзор

Распределенная система для реализации RAG (Retrieval-Augmented Generation) архитектуры. Система обрабатывает запросы через несколько независимых pipeline, используя очереди сообщений, векторный поиск и индексацию документов.

**Ключевая особенность**: Все взаимодействия между микросервисами проходят через `translator_service`, который служит единой точкой интеграции.

## Компоненты системы

Система состоит из 7 сервисов, работающих в Docker-контейнерах:

### Инфраструктурные сервисы

**artemis** (Apache ActiveMQ Artemis)
- Брокер сообщений (AMQP)
- Порты: 61616 (AMQP), 8161 (веб-консоль)
- Очереди: `chat.in`, `email.in`, `index.in` (входящие), `chat.out`, `email.out`, `index.out` (исходящие)

**redis**
- Хранилище очередей для асинхронной обработки
- Порт: 6379
- Очереди: `chats`, `email`

**opensearch**
- Векторная база данных для поиска
- Порт: 9200
- Индекс: `docs`

### Сервисы приложения

**file_service**
- HTTP-сервис для работы с файлами
- Порт: 9001
- Эндпоинты: `GET /files`, `GET /file/{name}`
- Технологии: FastAPI

**translator_service**
- Сервис-переходник (центральная точка интеграции)
- Порт: 8005
- Функции:
  - AMQP консьюмер: слушает очереди Artemis (`chat.in`, `email.in`, `index.in`)
  - Маршрутизация: направляет сообщения в Redis (для chat/email) или indexer_service (для index)
  - Прием результатов: получает результаты от `rag_service` и `indexer_service` через HTTP
  - Отправка в Artemis: пишет результаты в соответствующие OUT-очереди
  - Прямые API: предоставляет HTTP endpoints для обхода Artemis
- Эндпоинты:
  - `POST /ingest` - прием сообщений (для обратной совместимости)
  - `POST /chat` - прямой запрос на обработку чата
  - `POST /email` - прямой запрос на обработку email
  - `POST /index` - прямой запрос на индексацию
  - `POST /result/rag` - прием результатов от rag_service
  - `POST /result/indexer` - прием результатов от indexer_service
- Клиенты: `clients/redis.py`, `clients/artemis_producer.py`, `clients/artemis_consumer.py`, `clients/indexer_service_internal.py`
- Технологии: FastAPI, Redis, python-qpid-proton

**rag_service**
- Воркер для обработки RAG-запросов
- Функции:
  - Читает векторы из Redis-очередей (`chats`, `email`)
  - Выполняет KNN-поиск в OpenSearch по вектору запроса
  - Формирует ответ с найденным документом
  - Отправляет результат в `translator_service` через HTTP
- Клиенты: `clients/redis.py`, `clients/opensearch.py`, `clients/translator_service_internal.py`
- Технологии: Python, Redis, OpenSearch, TaskIQ

**indexer_service**
- Сервис индексации документов
- Порт: 8001
- Эндпоинт: `POST /index`
- Функции:
  - Получает список файлов из `file_service`
  - Читает содержимое файлов
  - Разбивает текст на чанки (фрагменты)
  - Генерирует векторные представления для каждого чанка
  - Сохраняет чанки с векторами в OpenSearch индекс `docs`
  - Отправляет результат индексации в `translator_service` через HTTP
- Клиенты: `clients/opensearch.py`, `clients/file_service_internal.py`, `clients/translator_service_internal.py`
- Технологии: FastAPI, OpenSearch, NumPy

## Потоки данных

### CHAT Pipeline

**Через Artemis:**
```
Клиент → Artemis (chat.in) → translator_service → Redis (chats) → rag_service → OpenSearch → rag_service → translator_service → Artemis (chat.out)
```

**Через HTTP API:**
```
Клиент → translator_service (/chat) → Redis (chats) → rag_service → OpenSearch → rag_service → translator_service → Artemis (chat.out)
```

### EMAIL Pipeline

Аналогично CHAT, но использует очередь `email.in` и Redis очередь `email`.

### INDEX Pipeline

**Через Artemis:**
```
Клиент → Artemis (index.in) → translator_service → indexer_service → file_service → indexer_service → OpenSearch → indexer_service → translator_service → Artemis (index.out)
```

**Через HTTP API:**
```
Клиент → translator_service (/index) → indexer_service → file_service → indexer_service → OpenSearch → indexer_service → translator_service → Artemis (index.out)
```

## Взаимодействие сервисов

### Схема зависимостей

```
artemis
  ├──→ translator_service (AMQP консьюмер)
  │     ├──→ Redis (chats/email) → rag_service → OpenSearch → translator_service (HTTP)
  │     ├──→ indexer_service (HTTP) → file_service → OpenSearch → translator_service (HTTP)
  │     └──→ Artemis (OUT очереди, AMQP producer)
```

### Матрица взаимодействий

| Сервис | Взаимодействует с | Протокол | Назначение |
|--------|-------------------|----------|------------|
| `translator_service` | `artemis` | AMQP | Чтение из `chat.in`, `email.in`, `index.in` |
| `translator_service` | `artemis` | AMQP | Отправка в `chat.out`, `email.out`, `index.out` |
| `translator_service` | `redis` | Redis | Запись в очереди `chats`, `email` |
| `translator_service` | `indexer_service` | HTTP | Запуск индексации |
| `translator_service` | `rag_service` | HTTP | Прием результатов обработки |
| `translator_service` | `indexer_service` | HTTP | Прием результатов индексации |
| `rag_service` | `redis` | Redis | Чтение из очередей `chats`, `email` |
| `rag_service` | `opensearch` | HTTP | KNN-поиск по векторам |
| `rag_service` | `translator_service` | HTTP | Отправка результатов обработки |
| `indexer_service` | `file_service` | HTTP | Получение списка и содержимого файлов |
| `indexer_service` | `opensearch` | HTTP | Сохранение индексированных документов |
| `indexer_service` | `translator_service` | HTTP | Отправка результата индексации |

## Типы данных

**Векторы**
- Формат: JSON-массив чисел
- Размерность: 10 чисел (VECTOR_DIM=10)
- Пример: `[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]`

**Документы в OpenSearch**
```json
{
  "doc_id": "имя_файла.txt",
  "chunk_id": 0,
  "content": "текст чанка",
  "vector": [0.1, 0.2, ...]
}
```
- Чанки: текст разбивается на фрагменты по 50 символов (CHUNK_SIZE=50)

**Сообщения в Artemis**
- Формат: текстовые сообщения (JSON или plain text)
- Очереди IN: принимают команды/запросы
- Очереди OUT: возвращают результаты

## Конфигурация

### Переменные окружения

**translator_service:**
- `REDIS_HOST`, `REDIS_PORT` - подключение к Redis
- `QUEUE_CHATS`, `QUEUE_EMAIL` - имена Redis-очередей
- `ARTEMIS_URL` - URL подключения к Artemis
- `ARTEMIS_QUEUE_*_IN` - имена входящих очередей
- `ARTEMIS_QUEUE_*_OUT` - имена исходящих очередей
- `INDEXER_URL` - URL indexer_service

**rag_service:**
- `REDIS_HOST`, `REDIS_PORT` - подключение к Redis
- `OPENSEARCH_HOST` - URL OpenSearch
- `INDEX_NAME` - имя индекса в OpenSearch
- `QUEUE_CHATS`, `QUEUE_EMAIL` - имена Redis-очередей
- `TRANSLATOR_SERVICE_URL` - URL translator_service

**indexer_service:**
- `OPENSEARCH_HOST` - URL OpenSearch
- `FILE_SERVICE_URL` - URL file_service
- `INDEX_NAME` - имя индекса в OpenSearch
- `TRANSLATOR_SERVICE_URL` - URL translator_service

## Веб-интерфейсы и мониторинг

**Artemis (веб-консоль)**
- URL: http://localhost:8161
- Логин/Пароль: `artemis` / `artemis`
- Разделы:
  - Queues - проверка наличия очередей и количества сообщений
  - Connections - активные подключения сервисов
  - Sessions - активные сессии AMQP

**OpenSearch**
- URL: http://localhost:9200
- Полезные endpoints:
  - `/_cat/indices?v` - список индексов
  - `/docs/_search?pretty=true` - поиск документов
  - `/docs/_mapping?pretty=true` - структура индекса
  - `/docs/_stats?pretty=true` - статистика индекса
  - `/docs/_count?pretty=true` - количество документов

**Redis**
- Доступ через командную строку:
  ```bash
  docker compose exec redis redis-cli
  ```
- Команды:
  - `LLEN chats` - длина очереди chats
  - `LLEN email` - длина очереди email
  - `LRANGE chats 0 -1` - просмотр всех сообщений в очереди chats
  - `KEYS *` - список всех ключей
