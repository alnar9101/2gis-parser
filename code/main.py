
import csv
import os
import time

from browser import create_driver
from search import search_organizations
from cards_list import (
    get_cards,
    scroll_until_end,
    go_to_next_page,
    get_card_urls,
)
from card_parser import parse_card
from storage import load_existing_data, append_organization
from rubrics import load_rubrics, build_rubric_url

# Загружаем рубрики из CSV
rubrics = load_rubrics("rubrics_mapping_updated.csv")

print(f"Загружено рубрик: {len(rubrics)}")
print("Первая рубрика:", rubrics[0])

driver = create_driver(headless=False)

results = load_existing_data("2gis_data.csv")

seen_ids = {row["id"] for row in results}

print(f"📂 Загружено ранее сохранённых организаций: {len(results)}")

page = 1
MAX_PAGES = 3

try:
    # 1. Открываем сайт
    # rubric = rubrics[0]

    rubric = next(
        r for r in rubrics
        if r["name"] == "Рестораны"
    )

    url = build_rubric_url(rubric["id"])

    print(f"Обрабатываем рубрику: {rubric['name']}")
    print(f"URL: {url}")

    driver.get(url)

    time.sleep(7)

    # driver.get("https://2gis.com/ekaterinburg")
    # time.sleep(7)
    #
    # # 2. Выполняем поиск
    # search_organizations(driver, "Пункты выдачи интернет-заказов")

    while True:
        # 3. Прокручиваем текущую страницу поиска
        scroll_until_end(driver)

        # 4. Получаем ссылки на организации
        card_urls = get_card_urls(driver)

        print(f"\n📄 Страница {page}")
        print(f"Карточек после скролла: {len(get_cards(driver))}")
        print(f"Получено уникальных ссылок: {len(card_urls)}")

        # Сохраняем адрес поисковой выдачи
        search_url = driver.current_url

        # 5. Обрабатываем организации
        for i, url in enumerate(card_urls, start=1):
            print(f"Обрабатываем {i}/{len(card_urls)}")
            firm_id = url.rstrip("/").split("/")[-1]

            if firm_id in seen_ids:
                print(f"⏭️ Организация {firm_id} уже сохранена. Пропускаем.")
                continue

            try:
                driver.get(url)
                data = parse_card(driver)

                if not data or data.get("id") is None:
                    print("⚠️ Не удалось получить ID организации")
                    continue

                if data["id"] in seen_ids:
                    print(f"⚠️ Повторная организация: {data['id']}")
                    continue

                append_organization("2gis_data.csv", data)

                seen_ids.add(data["id"])
                results.append(data)

                print(f"💾 Организация {data['id']} сохранена")

            except Exception as e:
                print(f"⚠️ Ошибка обработки {url}: {e}")

        # 6. Сохраняем накопленные результаты
        # if results:
        #     with open(
        #         "2gis_data.csv",
        #         "w",
        #         newline="",
        #         encoding="utf-8"
        #     ) as f:
        #         writer = csv.DictWriter(
        #             f,
        #             fieldnames=results[0].keys()
        #         )
        #         writer.writeheader()
        #         writer.writerows(results)

            print(f"💾 Сохранено организаций: {len(results)}")

        # 7. Проверяем лимит страниц
        if page >= MAX_PAGES:
            print(f"✅ Достигнут лимит: {MAX_PAGES} страниц")
            break

        # 8. Возвращаемся к поисковой выдаче
        driver.get(search_url)

        print("Сохранённый URL поиска:", search_url)
        print("Текущий URL браузера:", driver.current_url)
        print("Заголовок страницы:", driver.title)
        print("Количество карточек:", len(get_cards(driver)))

        # 9. Прокручиваем выдачу для доступа к пагинации
        scroll_until_end(driver)

        # 10. Переходим на следующую страницу
        if not go_to_next_page(driver):
            print("⚠️ Не удалось перейти на следующую страницу")
            break

        page += 1

finally:
    print("CSV сохраняется в:", os.path.abspath("2gis_data.csv"))
    print(f"Всего собрано организаций: {len(results)}")
    print("Количество уникальных ID:", len(seen_ids))
    driver.quit()































# import csv
# import os
# import time
# from browser import create_driver
# from search import search_organizations
# from cards_list import open_card_by_index, go_back, get_cards, scroll_until_end, go_to_next_page, get_card_urls
# from card_parser import parse_card
#
# driver = create_driver(headless=False)
#
# # 1. Открываем сайт
# driver.get("https://2gis.com/ekaterinburg")
# time.sleep(7)
#
# # 2. Поиск
# search_organizations(driver, "Пункты выдачи интернет-заказов")
#
# # 3. Скролл
# scroll_until_end(driver)
#
# # 4. Получаем карточки
# cards = get_cards(driver)
# total = len(cards)
#
# results = []
# seen_ids = set()
#
# page = 1
# MAX_PAGES = 2
#
# while True:
#     card_urls = get_card_urls(driver)
#
#     print(f"Получено уникальных ссылок: {len(card_urls)}")
#
#
#     print(f"\n📄 Страница {page}")
#
#     cards = get_cards(driver)
#     print("Карточек после скролла", len(cards))
#     total = len(cards)
#     search_url = driver.current_url
#
#     for i, url in enumerate(card_urls, start=1):
#         print(f"Обрабатываем {i}/{len(card_urls)}")
#
#         driver.get(url)
#
#         data = parse_card(driver)
#
#         if data["id"] is None:
#             print("⚠️ Не удалось получить ID организации")
#
#         elif data["id"] in seen_ids:
#             print(f"⚠️ Повторная организация: {data['id']}")
#
#         else:
#             seen_ids.add(data["id"])
#             results.append(data)
#
#     if page >= MAX_PAGES:
#         print(f"✅ Достигнут лимит: {MAX_PAGES} страниц")
#         break
#
#     scroll_until_end(driver)
#
#     if not go_to_next_page(driver):
#         print("⚠️ Не удалось перейти на следующую страницу")
#         break
#
#     page += 1
#
#     # Возвращаемся к поисковой выдаче после всех организаций
#     driver.get(search_url)
#
#     print("Сохранённый URL поиска:", search_url)
#     print("Текущий URL браузера:", driver.current_url)
#     print("Заголовок страницы:", driver.title)
#     print("Количество карточек:", len(get_cards(driver)))
#
#     # Проверяем лимит страниц
#     if page >= MAX_PAGES:
#         print(f"✅ Достигнут лимит: {MAX_PAGES} страниц")
#         break
#
#     # Прокручиваем список для загрузки пагинации
#     scroll_until_end(driver)
#
#     # Переходим на следующую страницу
#     if not go_to_next_page(driver):
#         print("⚠️ Не удалось перейти на следующую страницу")
#         break
#
#
#         # Сохраняем результаты после каждой страницы
#     if results:
#         with open("2gis_data.csv", "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=results[0].keys())
#             writer.writeheader()
#             writer.writerows(results)
#
#         print(f"💾 Сохранено организаций: {len(results)}")
#     if page >= MAX_PAGES:
#         print(f"✅ Достигнут лимит: {MAX_PAGES} страниц")
#         break
#     # 👉 Переход на следующую страницу
#     if not go_to_next_page(driver):
#         break
#
#     page += 1
# print("CSV сохраняется в:", os.path.abspath("2gis_data.csv"))
# # 6. Сохранение CSV
# if results:
#     with open("2gis_data.csv", "w", newline="", encoding="utf-8") as f:
#         writer = csv.DictWriter(f, fieldnames=results[0].keys())
#         writer.writeheader()
#         writer.writerows(results)
#
#
# print("✅ Данные сохранены в 2gis_data.csv")
#
# driver.quit()
#
#
# # for i in range(total):
#     #     print(f"Обрабатываем {i + 1}/{total}")
#     #     current_cards = [
#     #         card.get_attribute("textContent")[:80]
#     #         for card in get_cards(driver)
#     #     ]
#     #
#     #     if current_cards != original_cards:
#     #         print(f"⚠️ Список карточек изменился перед обработкой {i + 1}")
#     #     else:
#     #         print("Порядок карточек не изменился")
#     #
#     #     if not open_card_by_index(driver, i):
#     #         continue
#     #
#     #     time.sleep(2)
#     #
#     #     data = parse_card(driver)
#     #
#     #     if data["id"] is None:
#     #         print("⚠️ Не удалось получить ID организации")
#     #
#     #     elif data["id"] in seen_ids:
#     #         print(f"⚠️ Повторная организация: {data['id']}")
#     #
#     #     else:
#     #         seen_ids.add(data["id"])
#     #         results.append(data)