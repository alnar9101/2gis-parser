import csv
import json
import os

FIELDNAMES = [
    "id",
    "name",
    "display_category",
    "enterprise_type",
    "address",
    "district",
    "microdistrict",
    "email",
    "rubrics",
    "status",
    "cuisines",
]


def load_existing_data(filename):
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def append_organization(filename, data):
    file_exists = os.path.exists(filename)

    row = data.copy()
    row["cuisines"] = json.dumps(
        row.get("cuisines", []),
        ensure_ascii=False
    )

    if row.get("rubrics") is not None:
        row["rubrics"] = json.dumps(
            row["rubrics"],
            ensure_ascii=False
        )

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES
        )

        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow(row)