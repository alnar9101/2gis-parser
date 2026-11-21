from selenium.webdriver.common.by import By
from browser import create_driver
from cards_list import scroll_until_end, go_to_next_page
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

    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        "div._n5hmn94"
    )

    print(f"Найдено кнопок пагинации: {len(buttons)}")

    for button in buttons:
        print(button.get_attribute("outerHTML"))

    result = go_to_next_page(driver)

    print(f"Результат has_next_page(): {result}")

    if result is False:
        print("🏁 Кнопка «Вперёд» отсутствует")
    else:
        print("➡️ Кнопка «Вперёд» присутствует")

    print(f"Результат go_to_next_page(): {result}")

    if result is False:
        print("✅ Кнопка «Вперёд» не найдена")
    else:
        print("⚠️ Функция выполнила переход")

finally:
    driver.quit()