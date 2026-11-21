
from browser import create_driver
from cards_list import collect_page_urls
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

RUBRIC_ID = "164"
PAGE = 5

url = (
    "https://2gis.ru/ekaterinburg/search/"
    f"rubric/rubricId/{RUBRIC_ID}/page/{PAGE}"
)

driver = create_driver(headless=False)

try:
    driver.get(url)

    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div._1x4k6z7")
        )
    )

    urls = collect_page_urls(driver)

    print(f"\n📄 Страница: {PAGE}")
    print(f"URL: {driver.current_url}")
    print(f"Организаций: {len(urls)}")

    buttons = driver.find_elements(
        By.CSS_SELECTOR,
        "div._n5hmn94"
    )

    print(f"Кнопок пагинации: {len(buttons)}")

    for index, button in enumerate(buttons, start=1):
        print(f"\nКнопка {index}")
        print(button.get_attribute("outerHTML"))

finally:
    driver.quit()
