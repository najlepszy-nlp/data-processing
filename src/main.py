import logging
from fastapi import FastAPI
from gliner import GLiNER
import pandas as pd
from transformers import pipeline

from utils.gliner import process_row

INPUT_DATA_PATH = "/mnt/data/data.csv"

logging.basicConfig(level=logging.INFO)

_data: list[dict] = []

ner = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
qa_model_name = "deepset/roberta-base-squad2"
qa = pipeline("question-answering", model=qa_model_name, tokenizer=qa_model_name)

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "up"}


@app.get("/data")
async def data(skip: int = 0, limit: int = 10):
    return _data[skip : skip + limit]


@app.post("/processing")
async def processing():
    logging.info("Processing data...")

    df = pd.read_csv(INPUT_DATA_PATH, delimiter=";")

    global _data
    _data = []

    for i, row in df.head(n=30).iterrows():
        logging.info(f"Processing row {i + 1}/{len(df)}")
        _data.append(process_row(row, ner, qa))

    logging.info("Data processed.")
    return {"status": "done"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
