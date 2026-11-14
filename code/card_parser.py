import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def clean_text(text):
    if not text:
        return None

    return " ".join(text.split())


def parse_card(driver):
    data = {
        "id": None,
        "name": None,
        "address": None,
        "district": None,
        "microdistrict": None,
        "email": None,
        "rubrics": None,
        "status": "active",
    }

    # --- ID ---
    try:
        WebDriverWait(driver, 10).until(
            lambda d: "/firm/" in d.current_url
        )

        match = re.search(r"/firm/(\d+)", driver.current_url)

        if match:
            data["id"] = match.group(1)

    except Exception as e:
        print(f"Ошибка получения ID: {type(e).__name__}")

    # --- Название ---
    try:
        name = WebDriverWait(driver, 10).until(
            lambda d: (
                    d.find_element(By.TAG_NAME, "h1")
                    .get_attribute("textContent") or ""
            ).strip()
        )

        data["name"] = clean_text(name)


    except Exception as e:

        print(f"Ошибка получения названия: {type(e).__name__}")

        headings = driver.find_elements(By.TAG_NAME, "h1")

        for heading in headings:
            print("h1.text:", repr(heading.text))

            print(

                "h1.textContent:",

                repr(heading.get_attribute("textContent"))

            )

            print("h1.is_displayed:", heading.is_displayed())

    # --- Контейнер с адресной информацией ---
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div._8sgdp4")
            )
        )

        block = container.find_element(
            By.CSS_SELECTOR, "div._172gbf8"
        )

    except Exception as e:
        print(f"Ошибка поиска блока адреса: {type(e).__name__}")
        block = None

    if block is not None:

        # --- Адрес ---
        try:
            address = WebDriverWait(block, 10).until(
                lambda element: element.find_element(
                    By.CSS_SELECTOR,
                    "a[href*='geo']"
                ).get_attribute("textContent").strip()
            )

            data["address"] = clean_text(address)

        except Exception as e:
            print(f"Ошибка получения адреса: {type(e).__name__}")

        # --- Район и микрорайон ---
        try:
            district_text = WebDriverWait(block, 10).until(
                lambda element: element.find_element(
                    By.CSS_SELECTOR,
                    "div._1p8iqzw"
                ).get_attribute("textContent").strip()
            )

            parts = [
                clean_text(part).strip()
                for part in district_text.split(",")
            ]

            for part in parts:
                if part.endswith("район"):
                    data["district"] = part

                elif part.endswith("м-н"):
                    data["microdistrict"] = part

        except Exception as e:
            print(
                f"Ошибка получения района и микрорайона: "
                f"{type(e).__name__}"
            )

    # --- Электронная почта ---
    try:
        email_links = driver.find_elements(
            By.CSS_SELECTOR,
            "a[href^='mailto:']"
        )

        if email_links:
            email_href = email_links[0].get_attribute("href")

            if email_href:
                data["email"] = email_href.removeprefix("mailto:")

    except Exception as e:
        print(f"Ошибка получения email: {type(e).__name__}")

    # --- Рубрики организации ---
    try:
        info_tab = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//*[normalize-space(text())='Инфо']")
            )
        )

        info_tab.click()

        # Ждём появления раздела "В справочнике"
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[normalize-space(text())='В справочнике']"
                )
            )
        )

        # Даём время загрузиться всем рубрикам
        time.sleep(3)

        # Получаем ссылки на рубрики
        rubric_links = driver.find_elements(
            By.CSS_SELECTOR,
            "a[href*='/rubricId/']"
        )

        rubrics = []

        for link in rubric_links:
            rubric_name = clean_text(link.text)

            if rubric_name:
                rubrics.append(rubric_name)

        if rubrics:
            data["rubrics"] = "; ".join(dict.fromkeys(rubrics))

    except Exception as e:
        print(f"Ошибка получения рубрик: {type(e).__name__}")

    print(f"Итоговые данные: {data}")

    return data