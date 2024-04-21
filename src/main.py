from fastapi import FastAPI
from gliner import GLiNER
import pandas as pd

from utils.gliner import process_row_using_gliner

INPUT_DATA_PATH = "../data/data.csv"

_data: list[dict] = []


app = FastAPI()


@app.get("/")
async def root():
    return {"status": "up"}


@app.get("/data")
async def data():
    return _data


@app.post("/processing")
async def processing():
    model = GLiNER.from_pretrained("urchade/gliner_medium-v2.1")
    df = pd.read_csv(INPUT_DATA_PATH, delimiter=";")

    _data = []

    for i, row in df.iterrows():
        print(f"Processing row {i + 1}/{len(df)}")
        _data.append(process_row_using_gliner(row, model))
