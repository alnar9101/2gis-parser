import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import ElementClickInterceptedException

def clean_text(text):
    if not text:
        return None

    return " ".join(text.split())

def wait_for_rubrics(driver, timeout=15, stable_time=2):
    selector = "a[href*='/rubricId/']"

    start_time = time.monotonic()
    last_count = -1
    last_change = time.monotonic()

    while time.monotonic() - start_time < timeout:
        elements = driver.find_elements(
            By.CSS_SELECTOR,
            selector
        )

        count = len(elements)

        if count != last_count:
            last_count = count
            last_change = time.monotonic()

        if count > 0 and time.monotonic() - last_change >= stable_time:
            return elements

        time.sleep(0.3)

    return driver.find_elements(
        By.CSS_SELECTOR,
        selector
    )


def parse_card(driver):
    data = {
        "id": None,
        "name": None,
        "display_category": None,
        "enterprise_type": None,
        "cuisines": [],
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

    # --- Категория под названием организации ---
    try:
        category_elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span._3yxk2u"
        )

        for element in category_elements:
            category = clean_text(element.text)

            if category:
                data["display_category"] = category
                break

    except Exception as e:
        print(f"Ошибка получения категории: {type(e).__name__}")

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

        try:
            info_tab.click()

        except ElementClickInterceptedException:
            print("Вкладка Инфо перекрыта. Повторяем попытку.")

            time.sleep(1)

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
        start_rubrics = time.perf_counter()

        rubric_links = wait_for_rubrics(driver)

        print(
            f"Ожидание рубрик: "
            f"{time.perf_counter() - start_rubrics:.2f} сек."
        )
        rubrics = []
        seen_rubric_ids = set()

        for link in rubric_links:
            rubric_name = clean_text(
                link.get_attribute("textContent")
            )

            href = link.get_attribute("href")

            if not rubric_name or not href:
                continue

            match = re.search(r"/rubricId/(\d+)", href)

            if not match:
                continue

            rubric_id = match.group(1)

            if rubric_id in seen_rubric_ids:
                continue

            seen_rubric_ids.add(rubric_id)

            rubrics.append({
                "rubric_id": rubric_id,
                "name": rubric_name
            })

        if rubrics:
            data["rubrics"] = rubrics

        # --- Кухни организации ---
        cuisines = []

        # WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located(
        #         (By.CSS_SELECTOR, "span._wrdavn")
        #     )
        # )

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span._wrdavn"
        )

        for element in elements:
            cuisine = element.get_attribute("textContent")

            cuisine = cuisine.replace("\u200b", "").strip()

            # if cuisine.lower().endswith("кухня"):
            #     if cuisine not in cuisines:
            #         cuisines.append(cuisine)

            if cuisine.lower().endswith("кухня"):
                print(
                    "CUISINE DEBUG:",
                    data["name"],
                    repr(cuisine),
                    repr(element.get_attribute("outerHTML"))
                )

                if cuisine not in cuisines:
                    cuisines.append(cuisine)


        data["cuisines"] = cuisines



    except Exception as e:

        print(f"Ошибка получения рубрик: {type(e).__name__}")

        print(f"Подробности: {e}")



    # --- Тип предприятия ---
    try:
        labels = driver.find_elements(
            By.XPATH,
            "//span[normalize-space(.)='Тип предприятия']"
        )

        if labels:
            parent = labels[0].find_element(
                By.XPATH,
                "../.."
            )

            next_element = parent.find_element(
                By.XPATH,
                "following-sibling::*[1]"
            )

            data["enterprise_type"] = clean_text(
                next_element.get_attribute("textContent")
            )

    except Exception as e:
        print(f"Ошибка получения типа предприятия: {type(e).__name__}")

    print(f"Итоговые данные: {data}")
    # print("Название:", data.get("name"))
    # print("Рубрики:", data.get("rubrics"))
    # print("Кухни:", data.get("cuisines"))

    return data