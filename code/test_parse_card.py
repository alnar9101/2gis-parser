from browser import create_driver
from card_parser import parse_card
from storage import append_organization


def main():
    driver = create_driver(headless=False)

    try:
        driver.get(
            "https://2gis.ru/ekaterinburg/firm/70000001100183367"
        )

        data = parse_card(driver)
        append_organization("test_organizations.csv", data)

        print("Название:", data.get("name"))
        print("Рубрики:", data.get("rubrics"))
        print("Кухни:", data.get("cuisines"))

    finally:
        driver.quit()


if __name__ == "__main__":
    main()