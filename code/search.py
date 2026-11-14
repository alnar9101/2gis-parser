import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def search_organizations(driver, query):
    try:
        # Ждём поле поиска
        search_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input"))
        )

        search_input.clear()
        search_input.send_keys(query)
        time.sleep(1)

        # Enter
        search_input.send_keys(u'\ue007')

        # Ждём загрузку результатов
        time.sleep(5)

        print(f"✅ Поиск выполнен: {query}")

    except Exception as e:
        print(f"❌ Ошибка поиска: {e}")