import csv
import os


def load_existing_data(filename):
    if not os.path.exists(filename):
        return []

    with open(filename, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def append_organization(filename, data):
    file_exists = os.path.exists(filename)

    with open(filename, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())

        if not file_exists or os.path.getsize(filename) == 0:
            writer.writeheader()

        writer.writerow(data)