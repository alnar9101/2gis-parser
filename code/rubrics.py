import csv
from pathlib import Path


def load_rubrics(filename):
    rubrics = []

    with open(filename, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")

        for row in reader:
            rubrics.append({
                "id": row["rubric_id"],
                "name": row["rubric_name"],
            })

    return rubrics


def build_rubric_url(rubric_id):
    return (
        "https://2gis.ru/ekaterinburg/search/"
        f"rubric/rubricId/{rubric_id}"
    )