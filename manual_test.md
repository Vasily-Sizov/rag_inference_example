# Ручной запуск и проверка системы RAG

## Быстрый старт

```bash
# 1. Запустите все сервисы
docker compose up --build

# 2. Дождитесь запуска всех сервисов (30-60 секунд)

# 3. Запустите автоматические тесты
uv run python test_pipeline.py
```

Или используйте скрипт:
```bash
./run_tests.sh
```

## Запуск системы

```bash
docker compose up --build
```

Проверьте статус:
```bash
docker compose ps
```

Все сервисы должны быть в статусе `Up`:
- artemis (порт 8161, 61616)
- redis (порт 6379)
- translator_service (порт 8005)
- rag_service
- opensearch (порт 9200)
- file_service (порт 9001)
- indexer_service (порт 8001)

## Автоматическое тестирование

### Запуск тестов

```bash
# Через uv
uv run python test_pipeline.py

# Или через скрипт
./run_tests.sh
```

Отдельные pipeline:
```bash
uv run python test_pipeline.py chat    # Только chat pipeline
uv run python test_pipeline.py email   # Только email pipeline
uv run python test_pipeline.py index   # Только index pipeline
uv run python test_pipeline.py all     # Все pipeline (по умолчанию)
```

### Что делает тестовый скрипт

1. Проверяет доступность всех сервисов
2. Тестирует каждый pipeline двумя способами:
   - Через Artemis (отправка в очереди chat.in/email.in/index.in)
   - Через прямые HTTP API ручки translator_service
3. Тестирует INDEX pipeline: отправляет запрос на индексацию, проверяет создание индекса
4. Тестирует CHAT/EMAIL pipeline: отправляет тестовый вектор, проверяет обработку

## Проверка Artemis

Веб-консоль: http://localhost:8161

Логин/Пароль: `artemis` / `artemis`

Очереди:
- Входящие: `chat.in`, `email.in`, `index.in`
- Исходящие: `chat.out`, `email.out`, `index.out`

Примечание: translator_service автоматически слушает все входящие очереди через AMQP консьюмер.

## Ручная проверка CHAT Pipeline

### Через тестовый скрипт
```bash
uv run python test_pipeline.py chat
```

### Через Artemis
```bash
uv run python -c "
from proton import Message
from proton.reactor import Container
import json

class Sender:
    def on_start(self, event):
        conn = event.container.connect('amqp://artemis:artemis@localhost:61616')
        sender = event.container.create_sender(conn, 'chat.in')
        vector = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        sender.send(Message(body=json.dumps(vector)))
        conn.close()
        event.container.stop()

Container(Sender()).run()
"
```

### Через HTTP API
```bash
curl -X POST http://localhost:8005/chat \
  -H "Content-Type: application/json" \
  -d '{"body": "[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]"}'
```

### Внутренний pipeline

1. translator_service получает сообщение (через Artemis или HTTP API)
2. Кладёт вектор в Redis очередь `chats`
3. rag_service читает из Redis
4. Выполняет KNN-поиск в OpenSearch
5. Формирует ответ с найденным документом
6. Отправляет ответ в translator_service
7. translator_service отправляет результат в Artemis очередь `chat.out`

### Проверка результата

```bash
docker compose logs --tail=30 rag_service
docker compose logs --tail=30 translator_service
```

Ожидаемые логи:
- `Получено сообщение из Redis 'chats'`
- `Выполнение KNN-поиска по вектору`
- `Отправка ответа в translator_service из очереди chats`
- `Результат отправлен в chat.out`

## Ручная проверка EMAIL Pipeline

### Через тестовый скрипт
```bash
uv run python test_pipeline.py email
```

### Через HTTP API
```bash
curl -X POST http://localhost:8005/email \
  -H "Content-Type: application/json" \
  -d '{"body": "[0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.1]"}'
```

### Проверка результата
```bash
docker compose logs --tail=20 rag_service
docker compose logs --tail=20 translator_service
```

## Ручная проверка INDEX Pipeline

### Через тестовый скрипт
```bash
uv run python test_pipeline.py index
```

### Через HTTP API
```bash
curl -X POST http://localhost:8005/index
```

Или напрямую в indexer_service:
```bash
curl -X POST http://localhost:8001/index
```

### Внутренний pipeline

1. translator_service получает запрос (через Artemis или HTTP API)
2. Вызывает indexer_service через HTTP
3. indexer_service создаёт индекс `docs` в OpenSearch (если не существует)
4. Получает список файлов из file_service
5. Для каждого файла: скачивает содержимое, разбивает на чанки, генерирует векторы, сохраняет в OpenSearch
6. Отправляет результат в translator_service
7. translator_service отправляет результат в Artemis очередь `index.out`

### Проверка результата

```bash
docker compose logs --tail=40 indexer_service
docker compose logs --tail=20 translator_service
```

Проверьте данные в OpenSearch:
```bash
curl "http://localhost:9200/docs/_search?pretty=true"
```

Или в браузере: http://localhost:9200/docs/_search?pretty=true

## Проверка данных в OpenSearch

```bash
# Поиск всех документов
curl "http://localhost:9200/docs/_search?pretty=true"

# Проверка индекса
curl "http://localhost:9200/docs/_mapping?pretty=true"

# Статистика индекса
curl "http://localhost:9200/docs/_stats?pretty=true"

# Количество документов
curl "http://localhost:9200/docs/_count?pretty=true"
```

## Просмотр логов

```bash
# Все сервисы
docker compose logs -f

# Отдельные сервисы
docker compose logs -f rag_service
docker compose logs -f translator_service
docker compose logs -f indexer_service
docker compose logs -f file_service

# Последние N строк
docker compose logs --tail=50 rag_service
```

## Диагностика проблем

**Сервис не запускается:**
```bash
docker compose ps
docker compose logs <service_name>
docker compose restart <service_name>
```

**Ошибки импортов:**
```bash
ls */__init__.py
ls */clients/__init__.py
```

**OpenSearch не отвечает:**
```bash
curl http://localhost:9200
docker compose logs opensearch
```

**Redis недоступен:**
```bash
docker compose exec redis redis-cli ping
docker compose exec redis redis-cli LLEN chats
```

**Artemis недоступен:**
```bash
docker compose logs artemis
# Проверьте веб-консоль: http://localhost:8161
```

**translator_service не подключается к Artemis:**
```bash
docker compose logs translator_service | grep -i "artemis\|connected\|подписка"
```

## Очистка системы

```bash
# Остановка всех контейнеров
docker compose down

# Остановка и удаление томов
docker compose down -v

# Полная очистка (контейнеры, тома, образы)
docker compose down -v --rmi all
```

## Полезные команды

```bash
# Проверка статуса
docker compose ps

# Пересборка сервиса
docker compose build <service_name>
docker compose up -d <service_name>

# Просмотр использования ресурсов
docker stats

# Вход в контейнер
docker compose exec <service_name> /bin/bash

# Проверка API endpoints
curl http://localhost:8005/chat -X POST -H "Content-Type: application/json" -d '{"body":"[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]"}'
curl http://localhost:8005/email -X POST -H "Content-Type: application/json" -d '{"body":"[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]"}'
curl http://localhost:8005/index -X POST
curl http://localhost:8001/index -X POST
curl http://localhost:9001/files
```

## Технические детали

- Векторы: JSON-массивы из 10 чисел (VECTOR_DIM=10)
- Чанки: файлы разбиваются на чанки по 50 символов (CHUNK_SIZE=50)
- Индекс: название индекса в OpenSearch - `docs` (INDEX_NAME=docs)
- Порты:
  - translator_service: 8005
  - indexer_service: 8001
  - file_service: 9001
  - opensearch: 9200
  - artemis web: 8161
  - artemis amqp: 61616
  - redis: 6379

## Запуск тестов

Для запуска тестов используется `uv`:

```bash
# Установка зависимостей
uv sync --no-install-project

# Запуск тестов
uv run python test_pipeline.py

# Или через скрипт
./run_tests.sh
```

Все зависимости определены в `pyproject.toml` и устанавливаются изолированно в `.venv/`.
