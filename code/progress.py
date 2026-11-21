import json
import os


PROGRESS_FILE = "progress.json"


def load_progress():
    if not os.path.exists(PROGRESS_FILE):
        return None

    with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_progress(rubric_id, page, status="in_progress"):
    progress = {
        "rubric_id": str(rubric_id),
        "page": page,
        "status": status
    }

    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(
            progress,
            f,
            ensure_ascii=False,
            indent=4
        )

def complete_rubric(rubric_id, page):
    save_progress(
        rubric_id=rubric_id,
        page=page,
        status="completed"
    )