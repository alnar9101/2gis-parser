from selenium.webdriver.common.by import By

from browser import create_driver
from cards_list import scroll_until_end, go_to_next_page, get_card_urls
from rubrics import build_rubric_url

import time


RUBRIC_ID = "164"
MAX_TEST_PAGES = 5

driver = create_driver(headless=False)

try:
    driver.get(build_rubric_url(RUBRIC_ID))
    time.sleep(7)

    for page in range(1, MAX_TEST_PAGES + 1):

        print(f"\n========== СТРАНИЦА {page} ==========")

        scroll_until_end(driver)

        card_urls = get_card_urls(driver)

        print(f"Найдено организаций: {len(card_urls)}")

        buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "div._n5hmn94"
        )

        print(f"Элементов пагинации: {len(buttons)}")

        for i, button in enumerate(buttons, start=1):
            print(f"Кнопка {i}:")
            print(button.get_attribute("outerHTML"))

        if page == MAX_TEST_PAGES:
            print("Достигнут тестовый лимит")
            break

        if not go_to_next_page(driver):
            print("Переход недоступен")
            break

finally:
    driver.quit()