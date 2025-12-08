"""
HTTP-клиент для взаимодействия с file_service (внутренний клиент).
"""

import requests
from config import FILE_SERVICE_URL
from logger import logger

def list_files():
    response = requests.get(f"{FILE_SERVICE_URL}/files")
    response.raise_for_status()
    return response.json()

def fetch_file(name: str):
    logger.info(f"Fetching file: {name}")
    response = requests.get(f"{FILE_SERVICE_URL}/file/{name}")
    response.raise_for_status()
    return response.text

