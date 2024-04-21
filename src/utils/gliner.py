import datetime
import pandas as pd

from dateutil.parser import parse
from gliner import GLiNER


def process_row_using_gliner(row: pd.Series, model: GLiNER) -> list[dict]:
    LABELS = [
        "day when accident happened",
        "time when accident happened",
        "vehicle",
        "casualties",
    ]

    publish, place, text = row["Publish"], row["Place"], row["RAW_TEXT"]

    entities = model.predict_entities(text, LABELS)

    results = {
        "place": place,
        "date": None,
        "time": None,
        "vehicles": [],
        "casualties": 0,
    }

    seen_casualities = []

    for entity in entities:
        label, value = entity["label"], entity["text"]

        if label == "day when accident happened" and not results["date"]:
            try:
                publish_weekday = parse(publish).weekday()
                accident_weekday = parse(value.split(" ")[0]).weekday()
                results["date"] = (
                    parse(publish)
                    - datetime.timedelta(days=(publish_weekday - accident_weekday))
                ).strftime("%Y-%m-%d")
            except:
                pass

        elif label == "time when accident happened" and not results["time"]:
            results["time"] = value

        elif label == "vehicle" and value.lower() not in results["vehicles"]:
            results["vehicles"].append(value.lower())

        elif label == "casualties" and value.lower() not in seen_casualities:
            results["casualties"] += 1
            seen_casualities.append(value.lower())

    return results
