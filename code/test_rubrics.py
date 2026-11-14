
from browser import create_driver
from card_parser import parse_card

driver = create_driver(headless=False)

try:
    driver.get(
        "https://2gis.ru/ekaterinburg/firm/70000001019421352"
    )

    data = parse_card(driver)

    print("\nПолученные рубрики:")
    print(data["rubrics"])

finally:
    driver.quit()
