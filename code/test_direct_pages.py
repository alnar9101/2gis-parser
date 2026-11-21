import time

from browser import create_driver
from cards_list import scroll_until_end, get_card_urls

driver = create_driver(headless=False)

base_url = (
    "https://2gis.ru/ekaterinburg/"
    "search/restorany/rubricId/164"
)

pages = {}

try:
    for page in range(1, 4):
        url = base_url if page == 1 else f"{base_url}/page/{page}"

        driver.get(url)
        time.sleep(7)

        scroll_until_end(driver)

        from cards_list import get_cards

        cards = get_cards(driver)

        print(f"\n🔎 Страница {page}")
        print("Карточек в DOM:", len(cards))

        urls = get_card_urls(driver)
        print("Уникальных ссылок:", len(urls))

        ids = [url.rstrip("/").split("/")[-1] for url in urls]

        pages[page] = ids

        print(f"\n📄 СТРАНИЦА {page}")
        print("Количество:", len(ids))
        print("Первый ID:", ids[0] if ids else None)
        print("Последний ID:", ids[-1] if ids else None)

    print("\n🔎 ПРОВЕРКА ПЕРЕСЕЧЕНИЙ")

    for page in (1, 2):
        common = set(pages[page]) & set(pages[page + 1])

        print(
            f"Страницы {page} и {page + 1}: "
            f"повторяющихся организаций — {len(common)}"
        )

        if common:
            print("Повторяющиеся ID:", common)

finally:
    driver.quit()