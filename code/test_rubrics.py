from browser import create_driver
from card_parser import parse_card
from selenium.webdriver.common.by import By

driver = create_driver(headless=False)

try:
    driver.get(
        "https://2gis.ru/ekaterinburg/firm/70000001100183367"
    )

    data = parse_card(driver)
    rubrics = data["rubrics"]

    if rubrics:
        rubric_count = len(rubrics.split("; "))
    else:
        rubric_count = 0

    print(f"\nКоличество полученных рубрик: {rubric_count}")



finally:
    driver.quit()



# from browser import create_driver
# from card_parser import parse_card
# from selenium.webdriver.common.by import By
#
# driver = create_driver(headless=False)
#
# try:
#     driver.get(
#         "https://2gis.ru/ekaterinburg/firm/70000001100183367"
#     )
#
#     data = parse_card(driver)
#
#     print("\nПолученные рубрики:")
#     print(data["rubrics"])
#
#     category_elements = driver.find_elements(
#         By.CSS_SELECTOR,
#         "span._3yxk2u"
#     )
#
#     display_category = ""
#
#     for element in category_elements:
#         category = element.text.strip()
#
#         if category:
#             display_category = category
#             break
#
#     print("\nКатегория организации:")
#     print(display_category)
#
# finally:
#     driver.quit()




# from browser import create_driver
# from card_parser import parse_card
# from selenium.webdriver.common.by import By
#
# driver = create_driver(headless=False)
#
# try:
#     driver.get(
#         "https://2gis.ru/ekaterinburg/firm/70000001100183367"
#     )
#
#     data = parse_card(driver)
#
#     print("\nПолученные рубрики:")
#     print(data["rubrics"])
#
#     # Проверяем категорию под названием организации
#     category_elements = driver.find_elements(
#         By.CSS_SELECTOR,
#         "span._3yxk2u"
#     )
#
#     for element in category_elements:
#         category = element.text.strip()
#
#         if category:
#             print("Найдена категория:", category)
#
# finally:
#     driver.quit()
