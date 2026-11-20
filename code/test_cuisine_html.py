from browser import create_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


driver = create_driver(headless=False)

try:
    driver.get(
        "https://2gis.ru/ekaterinburg/firm/70000001105704871"
    )

    info_tab = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[normalize-space(text())='Инфо']")
        )
    )

    info_tab.click()

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.XPATH, "//*[normalize-space(text())='В справочнике']")
        )
    )

    elements = driver.find_elements(
        By.CSS_SELECTOR,
        "span._wrdavn"
    )

    for element in elements:
        text = element.get_attribute("textContent") or ""

        if "кухня" in text.lower():
            print("TEXT:", repr(text))
            print("HTML:", element.get_attribute("outerHTML"))
            print("-" * 50)

finally:
    driver.quit()