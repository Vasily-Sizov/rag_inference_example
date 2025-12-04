from fastapi import FastAPI
from indexer import run_indexing_pipeline
from logger import logger

app = FastAPI()

@app.post("/index")
def trigger_indexing():
    logger.info("Получен запрос на индексацию.")
    run_indexing_pipeline()
    return {"status": "accepted"}


