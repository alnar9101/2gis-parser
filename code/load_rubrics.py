import os
import requests
from dotenv import load_dotenv
import json
from pathlib import Path
load_dotenv()

API_KEY = os.getenv("DGIS_API_KEY")

url = "https://catalog.api.2gis.com/2.0/catalog/rubric/list"

params = {
    "region_id": 9,
    "fields": "items.rubrics",
    "locale": "ru_RU",
    "key": API_KEY,
}

file_path = Path(__file__).resolve().parent / "rubrics_2gis.json"

if file_path.exists():
    print("Загружаем справочник из локального файла")

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

else:
    print("Получаем справочник через API 2ГИС")

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

    print("Справочник сохранён")

categories = data["result"]["items"]

print("Количество категорий:", len(categories))

rubrics_count = sum(
    len(category.get("rubrics", []))
    for category in categories
)

print("Количество рубрик:", rubrics_count)
print("\nКатегории 2ГИС:")

for category in categories:
    print(category["id"], "-", category["name"])


