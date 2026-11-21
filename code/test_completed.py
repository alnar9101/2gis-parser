from browser import create_driver
from cards_list import scroll_until_end, go_to_next_page
from progress import save_progress, load_progress
import time

URL = (
    "https://2gis.ru/ekaterinburg/search/"
    "пункты%20выдачи%20заказов/page/292"
    "?m=60.599348%2C56.839856%2F15.93"
)

driver = create_driver(headless=False)

try:
    driver.get(URL)
    time.sleep(7)

    scroll_until_end(driver)

    if not go_to_next_page(driver):
        print("✅ Последняя страница определена")
        print("Здесь main.py должен сохранить статус completed")

finally:
    driver.quit()

import progress

progress.PROGRESS_FILE = "progress_test.json"

progress.complete_rubric(
    rubric_id="test_292",
    page=292
)

print("Сохранённый прогресс:", progress.load_progress())