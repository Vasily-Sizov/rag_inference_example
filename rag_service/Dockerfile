FROM python:3.11
WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn redis opensearch-py taskiq taskiq-redis numpy requests

CMD ["python", "worker.py"]

