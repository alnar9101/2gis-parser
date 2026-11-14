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
    except:
        print("❌ Контейнер не найден")
        return

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

        if len(buttons) == 0:
            return False
        # if len(buttons) < 2:
        #     return False

        next_button = buttons[-1] # последняя = вперед

        driver.execute_script("arguments[0].click();", next_button)
        time.sleep(5)

        print("➡️ Следующая страница")
        return True

    except:
        return False

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