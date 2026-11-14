import csv
from pathlib import Path

base_dir = Path(__file__).resolve().parent

source_path = base_dir / "rubrics_2gis.csv"
result_path = base_dir / "rubrics_mapping.csv"

with open(source_path, "r", encoding="utf-8-sig", newline="") as source:
    reader = csv.DictReader(source, delimiter=";")

    with open(result_path, "w", encoding="utf-8-sig", newline="") as result:
        fieldnames = [
            "rubric_id",
            "rubric_name",
            "parent_id",
            "parent_name",
            "activity_type",
            "object_type",
            "specialization",
            "review_status",
        ]

        writer = csv.DictWriter(
            result,
            fieldnames=fieldnames,
            delimiter=";"
        )

        writer.writeheader()

        for row in reader:
            writer.writerow({
                **row,
                "activity_type": "",
                "object_type": "",
                "specialization": "",
                "review_status": "Не проверено",
            })

print("Таблица классификации создана:", result_path)