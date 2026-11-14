from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless=False):
    """
    Создаёт и возвращает Chrome WebDriver
    """
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")

    if headless:
        options.add_argument("--headless=new")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


# ---------- УТИЛИТЫ ОЖИДАНИЯ ----------

def wait_for_element(driver, by, value, timeout=15):
    """
    Ждёт появления элемента на странице
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    except TimeoutException:
        return None


def wait_for_elements(driver, by, value, timeout=15):
    """
    Ждёт появления хотя бы одного элемента
    """
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_all_elements_located((by, value))
        )
    except TimeoutException:
        return []


def click_when_clickable(driver, by, value, timeout=15):
    """
    Ждёт, пока элемент станет кликабельным
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        return True
    except TimeoutException:
        return False