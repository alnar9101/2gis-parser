import csv
import json
from pathlib import Path

base_dir = Path(__file__).resolve().parent

json_path = base_dir / "rubrics_2gis.json"
csv_path = base_dir / "rubrics_2gis.csv"

with open(json_path, "r", encoding="utf-8") as file:
    data = json.load(file)

categories = data["result"]["items"]

with open(csv_path, "w", encoding="utf-8-sig", newline="") as file:
    writer = csv.writer(file, delimiter=";")

    writer.writerow([
        "rubric_id",
        "rubric_name",
        "parent_id",
        "parent_name",
    ])

    for category in categories:
        for rubric in category.get("rubrics", []):
            writer.writerow([
                rubric["id"],
                rubric["name"],
                rubric.get("parent_id", category["id"]),
                category["name"],
            ])

print("CSV-файл создан:", csv_path)
print("\nРубрики категории «Одежда / Обувь»:")

for category in categories:
    if category["id"] == "1035":
        for rubric in category.get("rubrics", []):
            print(rubric["id"], "-", rubric["name"])