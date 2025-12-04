FROM python:3.11
WORKDIR /app

COPY . .

RUN pip install fastapi uvicorn redis opensearch-py taskiq taskiq-redis numpy python-qpid-proton

CMD ["python", "worker.py"]
