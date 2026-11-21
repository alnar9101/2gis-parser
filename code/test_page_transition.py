from selenium.webdriver.common.by import By
import time

from browser import create_driver
from cards_list import (
    scroll_until_end,
    go_to_next_page,
    get_card_urls, get_cards,
)

driver = create_driver(headless=False)

try:
    url = "https://2gis.ru/ekaterinburg/search/rubric/rubricId/164"

    driver.get(url)
    time.sleep(7)

    # Первая страница
    scroll_until_end(driver)
    page_1_urls = get_card_urls(driver)

    print("\nСТРАНИЦА 1")
    print("Количество:", len(page_1_urls))
    print("Последний ID:", page_1_urls[-1].split("/")[-1])

    # Переход на вторую страницу

    driver.get(
        "https://2gis.ru/ekaterinburg/search/restorany/rubricId/164/page/3"
    )

    time.sleep(7)
    scroll_until_end(driver)

    # if not go_to_next_page(driver):
    #     raise RuntimeError("Вторая страница недоступна")
    print("\n🔎 СОСТОЯНИЕ ПОСЛЕ ПЕРЕХОДА")
    print("URL:", driver.current_url)
    print("Заголовок:", driver.title)

    print(
        "Текст пагинации:",
        driver.find_element(
            By.CSS_SELECTOR,
            "div._1x4k6z7"
        ).text[-500:]
    )

    # Список сразу после перехода
    print("\nСТРАНИЦА 2 — первый замер")
    urls_1 = get_card_urls(driver)

    for i, url in enumerate(urls_1, 1):
        print(i, url)

    # Ждём ещё 5 секунд
    time.sleep(5)

    scroll_until_end(driver)

    print("\n🔎 НАЗВАНИЯ КАРТОЧЕК В DOM")

    cards = get_cards(driver)

    for i, card in enumerate(cards, start=1):
        print(
            f"{i}.",
            repr(card.get_attribute("textContent")[:150])
        )

    # Повторно получаем список
    print("\nСТРАНИЦА 2 — второй замер")
    urls_2 = get_card_urls(driver)

    for i, url in enumerate(urls_2, 1):
        print(i, url)

    print("\nРЕЗУЛЬТАТ")
    print("Первый замер:", len(urls_1))
    print("Второй замер:", len(urls_2))
    print("Списки одинаковые:", urls_1 == urls_2)

    from selenium.webdriver.common.by import By

    print("\n🔎 ДИАГНОСТИКА DOM")

    cards = driver.find_elements(
        By.CSS_SELECTOR,
        "div._1kf6gff"
    )

    print("Всего элементов:", len(cards))

    for i, card in enumerate(cards, start=1):
        links = card.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/firm/']"
        )

        hrefs = [
            link.get_attribute("href").split("?")[0]
            for link in links
        ]

        print(
            f"{i}. "
            f"Виден: {card.is_displayed()}, "
            f"Ссылок: {len(hrefs)}, "
            f"URL: {hrefs}"
        )

finally:
    driver.quit()