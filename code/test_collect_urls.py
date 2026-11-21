
from browser import create_driver
from cards_list import collect_page_urls
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = "https://2gis.ru/ekaterinburg/search/rubric/rubricId/164"

driver = create_driver(headless=False)

try:
    driver.get(URL)

    print("⏳ Ожидаем загрузку списка организаций...")

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div._1x4k6z7")
        )
    )

    print("✅ Контейнер списка найден")

    urls = collect_page_urls(driver)

    print("\n📊 РЕЗУЛЬТАТ ПРОВЕРКИ")
    print(f"Получено уникальных ссылок: {len(urls)}")

    for index, url in enumerate(urls, start=1):
        print(f"{index}. {url}")

    if len(urls) == 12:
        print("✅ Получены все 12 ожидаемых ссылок")
    else:
        print("⚠️ Получено меньше 12 ссылок — нужна диагностика")

finally:
    driver.quit()
