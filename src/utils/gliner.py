import datetime
from dateutil.parser import parse

import pandas as pd
from transformers import Pipeline
from gliner import GLiNER


def ask_questions(qa: Pipeline, context: str):
    results = [None] * 5

    # Initial question
    question_what_happened = {"question": "What happened?", "context": context}
    answer_what_happened = qa(question_what_happened)
    results[2] = answer_what_happened["answer"]

    # Questions about what happened before
    question_before_1 = {
        "question": f'What happened before {answer_what_happened["answer"]}?',
        "context": context,
    }
    answer_before_1 = qa(question_before_1)
    results[1] = answer_before_1["answer"]

    question_before_2 = {
        "question": f'What happened before {answer_before_1["answer"]}?',
        "context": context,
    }
    answer_before_2 = qa(question_before_2)
    results[0] = answer_before_2["answer"]

    # Questions about what happened after
    question_after_1 = {
        "question": f'What happened after {answer_what_happened["answer"]}?',
        "context": context,
    }
    answer_after_1 = qa(question_after_1)
    results[3] = answer_after_1["answer"]

    question_after_2 = {
        "question": f'What happened after {answer_after_1["answer"]}?',
        "context": context,
    }
    answer_after_2 = qa(question_after_2)
    results[4] = answer_after_2["answer"]

    return results


def process_row(row: pd.Series, ner: GLiNER, qa: Pipeline):
    LABELS = [
        "day when accident happened",
        "time when accident happened",
        "vehicle",
        "casualties",
        "age of people who died",
    ]

    publish, place, text = row["Publish"], row["Place"], row["RAW_TEXT"]

    entities = ner.predict_entities(text, LABELS)

    results = {
        "place": place,
        "date": None,
        "time": None,
        "vehicles": [],
        "casualties": 0,
        "ageOfCasualties": [],
        "injuries": 0,
        "reason": "",
        "sequenceOfEvents": [],
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
        elif label == "age of people who died":
            results["ageOfCasualties"].append(value)
    question_reason = {"question": "How did the vehicle crash?", "context": text}
    answer_reason = qa(question_reason)

    question_injuries = {"question": "How many people were injured?", "context": text}
    answer_injuries = qa(question_injuries)

    results["injuries"] = answer_injuries["answer"]
    results["reason"] = answer_reason["answer"]
    results["sequenceOfEvents"] = ask_questions(qa, text)

    return results
