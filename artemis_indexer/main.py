"""
Точка входа сервиса indexer_consumer.

Здесь запускается AMQP-консьюмер, слушающий очередь index.in.
"""

from consumer import start_consumer

if __name__ == "__main__":
    start_consumer()
