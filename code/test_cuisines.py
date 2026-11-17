from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from browser import create_driver


def main():
    driver = create_driver(headless=False)

    try:
        # Открываем карточку ресторана
        driver.get(
            "https://2gis.ru/ekaterinburg/firm/70000001081874381"
        )

        # Открываем вкладку "Инфо"
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

        # Находим элементы с характеристиками
        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "span._wrdavn"
        )

        print("Найдено характеристик:", len(elements))

        cuisines = []

        for element in elements:
            text = element.get_attribute("textContent")

            # Удаляем невидимый символ
            text = text.replace("\u200b", "").strip()

            # Оставляем только названия кухонь
            if text.lower().endswith("кухня"):
                if text not in cuisines:
                    cuisines.append(text)

        print("Кухни:", cuisines)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()