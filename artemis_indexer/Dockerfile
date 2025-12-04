FROM python:3.11
WORKDIR /app

COPY . .

RUN pip install python-qpid-proton requests

CMD ["python", "main.py"]
