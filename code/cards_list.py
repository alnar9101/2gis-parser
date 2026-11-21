import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_cards(driver):
    try:
        cards = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div._1kf6gff"))
        )
        return cards
    except:
        return []


def open_card_by_index(driver, index):
    cards = get_cards(driver)

    if index >= len(cards):
        return False

    try:
        driver.execute_script("arguments[0].click();", cards[index])
        return True
    except:
        return False


def go_back(driver):
    driver.back()
    time.sleep(3)


def scroll_until_end(driver, pause_time=2):
    """
    Реальный рабочий скролл для 2GIS
    """
    import time
    from selenium.webdriver.common.by import By

    try:
        container = driver.find_element(By.CSS_SELECTOR, "div._1x4k6z7")

    except Exception as e:
        print(f"❌ Не удалось найти контейнер списка: {e}")
        raise

    last_height = 0

    while True:
        # текущая высота
        height = driver.execute_script(
            "return arguments[0].scrollTop", container
        )

        # скроллим немного вниз
        driver.execute_script(
            "arguments[0].scrollTop = arguments[0].scrollTop + 300",
            container
        )

        time.sleep(pause_time)

        new_height = driver.execute_script(
            "return arguments[0].scrollTop", container
        )

        # если не двигается — конец
        if new_height == height:
            break

    print("✅ Доскроллили до конца списка")

def go_to_next_page(driver):
    from selenium.webdriver.common.by import By
    import time

    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "div._n5hmn94")
        print(f"Найдено элементов пагинации: {len(buttons)}")
        for button in buttons:
            print("HTML элемента:", button.get_attribute("outerHTML"))

        next_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            'div._n5hmn94:has(svg[style*="rotate(-90deg)"])'
        )

        if not next_buttons:
            back_buttons = driver.find_elements(
                By.CSS_SELECTOR,
                'div._n5hmn94:has(svg[style*="rotate(90deg)"])'
            )

            if back_buttons:
                print("🏁 Обнаружена последняя страница")
                return False

            raise RuntimeError(
                "Не удалось определить состояние пагинации"
            )

        next_button = next_buttons[0]

        # if len(buttons) == 0:
        #     return False
        # # if len(buttons) < 2:
        # #     return False
        #
        # next_button = buttons[-1] # последняя = вперед

        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)

        print("➡️ Следующая страница")
        return True


    except Exception as e:

        print(f"❌ Ошибка при переходе на следующую страницу: {e}")

        raise

def get_card_urls(driver):
    cards = get_cards(driver)
    urls = []

    for card in cards:
        try:
            link = card.find_element(
                By.CSS_SELECTOR,
                "a[href*='/firm/']"
            )

            href = link.get_attribute("href")

            if href:
                url = href.split("?")[0]
                urls.append(url)

        except Exception as e:
            print(
                f"Не удалось получить ссылку: "
                f"{type(e).__name__}"
            )

    return list(dict.fromkeys(urls))


def collect_page_urls(driver, expected_count=12, attempts=3):
    """
    Собирает ссылки организаций после прокрутки.
    Повторяет попытку, если карточек меньше ожидаемого.
    """

    best_urls = []

    for attempt in range(1, attempts + 1):
        print(f"🔎 Попытка загрузки {attempt}/{attempts}")

        scroll_until_end(driver)

        urls = get_card_urls(driver)

        print(f"Получено уникальных ссылок: {len(urls)}")

        if len(urls) > len(best_urls):
            best_urls = urls

        if len(best_urls) >= expected_count:
            return best_urls

        if attempt < attempts:
            print("⏳ Карточек меньше ожидаемого. Повторяем...")
            time.sleep(3)

    return best_urls


def has_next_page(driver):
    next_buttons = driver.find_elements(
        By.CSS_SELECTOR,
        'div._n5hmn94:has(svg[style*="rotate(-90deg)"])'
    )

    if next_buttons:
        return True

    back_buttons = driver.find_elements(
        By.CSS_SELECTOR,
        'div._n5hmn94:has(svg[style*="rotate(90deg)"])'
    )

    if back_buttons:
        return False

    raise RuntimeError(
        "Не удалось определить состояние пагинации"
    )