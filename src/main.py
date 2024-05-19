import logging
import jsonlines
from fastapi import FastAPI
from gliner import GLiNER
import pandas as pd
from transformers import pipeline

from utils.processing import process_row

INPUT_DATA_PATH = "/mnt/data/data.csv"
INPUT_CITIES_PATH = "/mnt/data/cities.csv"
OUTPUT_DATA_PATH = "/mnt/data/data_processed.jsonl"

logging.basicConfig(level=logging.INFO)

_data: list[dict] = []

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "up"}


@app.get("/data")
async def data(skip: int = 0, limit: int = 10):
    global _data
    if not _data:
        with jsonlines.open(OUTPUT_DATA_PATH) as reader:
            _data = list(reader.iter())

    return _data[skip : skip + limit]


@app.post("/processing")
async def processing():
    logging.info("Loading models...")
    ner = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
    qa_model_name = "deepset/roberta-base-squad2"
    qa = pipeline("question-answering", model=qa_model_name, tokenizer=qa_model_name)
    logging.info("Models loaded.")

    logging.info("Processing data...")

    data_df = pd.read_csv(INPUT_DATA_PATH, delimiter=";")
    cities_df = pd.read_csv(INPUT_CITIES_PATH, delimiter=",")

    global _data
    _data = []

    for i, row in data_df.head(n=30).iterrows():
        logging.info(f"Processing row {i + 1}/{len(data_df)}")
        _data.append(process_row(row, ner, qa, cities_df))

    with jsonlines.open(OUTPUT_DATA_PATH, "w") as writer:
        writer.write_all(_data)

    logging.info("Data processed.")

    return {"status": "done"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
