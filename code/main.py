import os
import time

from progress import load_progress, save_progress, complete_rubric
from browser import create_driver
from cards_list import (
    get_cards,
    scroll_until_end,
    go_to_next_page,
    get_card_urls,
    collect_page_urls,
    has_next_page
)
from card_parser import parse_card
from storage import load_existing_data, append_organization
from rubrics import load_rubrics, build_rubric_url, build_page_url
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


# 1. Загружаем рубрики
rubrics = load_rubrics("rubrics_mapping_updated.csv")

print(f"Загружено рубрик: {len(rubrics)}")
print("Первая рубрика:", rubrics[0])


# 2. Загружаем ранее сохранённые организации
results = load_existing_data("2gis_data.csv")
seen_ids = {str(row["id"]) for row in results}

print(f"📂 Загружено ранее сохранённых организаций: {len(results)}")


# 3. Ограничение для тестирования
MAX_PAGES = 2

driver = create_driver(headless=False)

try:
    # 4. Выбираем рубрику для тестирования
    rubric = next(
        r for r in rubrics
        if r["name"] == "Рестораны"
    )

    # 5. Восстанавливаем прогресс
    progress = load_progress()

    page = 1

    if progress and progress["rubric_id"] == str(rubric["id"]):

        if progress.get("status") == "completed":
            print(f"✅ Рубрика «{rubric['name']}» уже завершена")
            print("Повторная обработка не требуется")

            raise SystemExit

        page = progress["page"]

    print(f"📂 Сохранённый прогресс: {progress}")
    print(f"📄 Требуется продолжить со страницы: {page}")

    # 6. Формируем URL сохранённой страницы
    page_url = build_page_url(rubric["id"], page)

    print(f"Обрабатываем рубрику: {rubric['name']}")
    print(f"URL страницы: {page_url}")

    # 7. Открываем сохранённую страницу напрямую
    driver.get(page_url)

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div._1x4k6z7")
            )
        )

    except TimeoutException:
        page_text = driver.find_element(
            By.TAG_NAME, "body"
        ).text.lower()

        if (
                "подозрительную активность" in page_text
                or "не робот" in page_text
                or "captcha" in page_text
        ):
            raise RuntimeError(
                "2ГИС запросил CAPTCHA. "
                "Парсер остановлен, прогресс сохранён."
            )

        raise RuntimeError(
            "Не удалось загрузить список организаций за 30 секунд."
        )

    print(f"✅ Открыта страница {page}")

    # 8. Основной цикл обработки страниц
    processed_pages = 0
    card_urls = None

    while True:

        # Прокручиваем страницу поиска
        if card_urls is None:
            card_urls = collect_page_urls(driver)


        # Проверяем наличие следующей страницы
        next_page_exists = has_next_page(driver)

        print(f"➡️ Есть следующая страница: {next_page_exists}")

        # Проверяем, что ссылки вообще получены
        if not card_urls:
            raise RuntimeError(
                f"На странице {page} не найдено организаций"
            )

        # Для промежуточной страницы проверяем полноту загрузки
        if next_page_exists and len(card_urls) < 12:
            raise RuntimeError(
                f"На странице {page} получено только "
                f"{len(card_urls)} организаций из ожидаемых 12"
            )

        # Последняя страница может содержать меньше 12 организаций
        if not next_page_exists:
            print(f"🏁 Последняя страница рубрики: {page}")



        print(f"\n📄 Страница {page}")
        print(f"Карточек после скролла: {len(get_cards(driver))}")
        print(f"Получено уникальных ссылок: {len(card_urls)}")

        # Запоминаем URL текущей страницы выдачи
        search_url = driver.current_url

        # 9. Обрабатываем организации
        # список проблемных карточек
        failed_urls = []
        for i, url in enumerate(card_urls, start=1):
            print(f"Обрабатываем {i}/{len(card_urls)}")

            firm_id = url.rstrip("/").split("/")[-1]

            if firm_id in seen_ids:
                print(
                    f"⏭️ Организация {firm_id} уже сохранена. "
                    f"Пропускаем."
                )
                continue

            try:
                # driver.get(url)
                #
                # data = parse_card(driver)

                start_time = time.perf_counter()

                driver.get(url)

                load_time = time.perf_counter() - start_time

                data = parse_card(driver)

                total_time = time.perf_counter() - start_time

                print(f"Загрузка страницы: {load_time:.2f} сек.")
                print(f"Парсинг карточки: {total_time - load_time:.2f} сек.")
                print(f"Общее время: {total_time:.2f} сек.")

                if not data or data.get("id") is None:
                    print("⚠️ Не удалось получить ID организации")
                    failed_urls.append(url)
                    continue

                if str(data["id"]) != str(firm_id):
                    print(
                        f"⚠️ Несовпадение ID: "
                        f"в ссылке {firm_id}, "
                        f"в карточке {data['id']}"
                    )
                    failed_urls.append(url)
                    continue

                if str(data["id"]) in seen_ids:
                    print(f"⚠️ Повторная организация: {data['id']}")
                    continue

                # Сохраняем организацию сразу после обработки
                append_organization("2gis_data.csv", data)

                seen_ids.add(str(data["id"]))
                results.append(data)

                print(f"💾 Организация {data['id']} сохранена")

            except Exception as e:
                print(f"⚠️ Ошибка обработки {url}: {e}")
                failed_urls.append(url)

            print(f"💾 Сохранено организаций: {len(results)}")


        # 11. Проверяем лимит страниц
        if failed_urls:
            print(f"❌ Не удалось обработать организаций: {len(failed_urls)}")

            for failed_url in failed_urls:
                print(f"   {failed_url}")

            raise RuntimeError(
                f"Обработка страницы {page} завершилась с ошибками"
            )
        processed_pages += 1

        # Если обработана последняя страница рубрики
        if not next_page_exists:
            save_progress(
                rubric["id"],
                page,
                "completed"
            )

            print(
                f"✅ Обработка рубрики «{rubric['name']}» завершена"
            )
            print(f"🏁 Последняя обработанная страница: {page}")

            break

        # if processed_pages >= MAX_PAGES:
        #     print(f"🛑 Достигнут тестовый лимит: {MAX_PAGES} страниц за запуск")
        #     break

        # 12. Проверяем тестовый лимит страниц
        if processed_pages >= MAX_PAGES:
            next_page = page + 1

            save_progress(rubric["id"], next_page, "in_progress")

            print(
                f"💾 Прогресс сохранён: "
                f"рубрика {rubric['id']}, "
                f"следующая страница {next_page}"
            )

            print(
                f"🛑 Достигнут тестовый лимит: "
                f"{MAX_PAGES} страниц за запуск"
            )
            break

        # 13. Формируем адрес следующей страницы
        next_page = page + 1
        next_page_url = build_page_url(rubric["id"], next_page)

        print(f"➡️ Переходим на страницу {next_page}")
        print(f"URL: {next_page_url}")

        # 14. Открываем следующую страницу напрямую
        driver.get(next_page_url)

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div._1x4k6z7")
                )
            )

        except TimeoutException:
            page_text = driver.find_element(
                By.TAG_NAME, "body"
            ).text.lower()

            if (
                    "подозрительную активность" in page_text
                    or "не робот" in page_text
                    or "captcha" in page_text
            ):
                raise RuntimeError(
                    "2ГИС запросил CAPTCHA. "
                    "Парсер остановлен."
                )

            raise RuntimeError(
                f"Не удалось загрузить страницу {next_page} за 30 секунд."
            )

        print(f"Текущий URL браузера: {driver.current_url}")

        # 15. Проверяем, что открылась нужная страница
        if f"/page/{next_page}" not in driver.current_url:
            raise RuntimeError(
                f"Не удалось открыть страницу {next_page}"
            )

        # 16. Проверяем наличие карточек
        next_card_urls = collect_page_urls(driver)

        if not next_card_urls:
            raise RuntimeError(
                f"На странице {next_page} не найдены организации. "
                "Необходимо проверить, достигнут ли конец рубрики."
            )

        print(
            f"✅ Открыта страница {next_page}. "
            f"Найдено организаций: {len(next_card_urls)}"
        )

        # Проверяем, что список организаций изменился
        previous_ids = {
            url.rstrip("/").split("/")[-1]
            for url in card_urls
        }

        next_ids = {
            url.rstrip("/").split("/")[-1]
            for url in next_card_urls
        }

        if previous_ids == next_ids:
            raise RuntimeError(
                f"На странице {next_page} получен тот же список "
                f"организаций, что и на странице {page}"
            )

        print("✅ Список организаций изменился")

        # 17. Сохраняем прогресс
        page = next_page

        card_urls = next_card_urls

        save_progress(rubric["id"], page, "in_progress")

        print(
            f"💾 Прогресс сохранён: "
            f"рубрика {rubric['id']}, "
            f"следующая страница {page}"
        )

finally:
    print("CSV сохраняется в:", os.path.abspath("2gis_data.csv"))
    print(f"Всего собрано организаций: {len(results)}")
    print("Количество уникальных ID:", len(seen_ids))

    driver.quit()





           # работа через кнопку
#         # 12. Возвращаемся к поисковой выдаче
#         driver.get(search_url)
#
#         print("Сохранённый URL поиска:", search_url)
#         print("Текущий URL браузера:", driver.current_url)
#         print("Заголовок страницы:", driver.title)
#         print("Количество карточек:", len(get_cards(driver)))
#
#         # 13. Прокручиваем выдачу
#         scroll_until_end(driver)
#
#         # 14. Запоминаем организации текущей страницы
#         previous_card_ids = {
#             url.rstrip("/").split("/")[-1]
#             for url in card_urls
#         }
#
#         # 15. Переходим на следующую страницу
#         if not go_to_next_page(driver):
#             complete_rubric(rubric["id"], page)
#             print(f"✅ Рубрика «{rubric['name']}» полностью обработана")
#             break
#
#         # 16. Ожидаем изменения списка организаций
#         next_card_urls = []
#
#         for attempt in range(20):
#             next_card_urls = get_card_urls(driver)
#
#             next_card_ids = {
#                 url.rstrip("/").split("/")[-1]
#                 for url in next_card_urls
#             }
#
#             if next_card_ids and next_card_ids != previous_card_ids:
#                 print("✅ Список организаций изменился")
#
#                 print("🔎 Ссылки сразу после перехода:")
#                 for index, card_url in enumerate(next_card_urls, start=1):
#                     print(f"{index}. {card_url}")
#                 break
#
#             time.sleep(0.5)
#
#         else:
#             raise RuntimeError(
#                 "После перехода список организаций не изменился"
#             )
#
#         # 17. Сохраняем прогресс
#         page += 1
#
#         save_progress(rubric["id"], page, "in_progress")
#
#         print(
#             f"💾 Прогресс сохранён: "
#             f"рубрика {rubric['id']}, "
#             f"следующая страница {page}"
#         )
#
#         # 18. Проверяем тестовый лимит страниц
#         if processed_pages >= MAX_PAGES:
#             print(
#                 f"🛑 Достигнут тестовый лимит: "
#                 f"{MAX_PAGES} страниц за запуск"
#             )
#             break
#
#         # # 14. Переходим на следующую страницу
#         # if not go_to_next_page(driver):
#         #     print("⚠️ Не удалось перейти на следующую страницу")
#         #     break
#         #
#         # page += 1
#         #
#         # # 15. Сохраняем прогресс после перехода
#         # save_progress(rubric["id"], page, "in_progress")
#         #
#         # print(
#         #     f"💾 Прогресс сохранён: "
#         #     f"рубрика {rubric['id']}, "
#         #     f"следующая страница {page}"
#         # )
#
# finally:
#     print("CSV сохраняется в:", os.path.abspath("2gis_data.csv"))
#     print(f"Всего собрано организаций: {len(results)}")
#     print("Количество уникальных ID:", len(seen_ids))
#
#     driver.quit()


















# from progress import load_progress, save_progress
# import csv
# import os
# import time
#
# from browser import create_driver
# from search import search_organizations
# from cards_list import (
#     get_cards,
#     scroll_until_end,
#     go_to_next_page,
#     get_card_urls,
# )
# from card_parser import parse_card
# from storage import load_existing_data, append_organization
# from rubrics import load_rubrics, build_rubric_url
#
# # Загружаем рубрики из CSV
# rubrics = load_rubrics("rubrics_mapping_updated.csv")
#
# print(f"Загружено рубрик: {len(rubrics)}")
# print("Первая рубрика:", rubrics[0])
#
# driver = create_driver(headless=False)
#
# results = load_existing_data("2gis_data.csv")
#
# seen_ids = {row["id"] for row in results}
#
# print(f"📂 Загружено ранее сохранённых организаций: {len(results)}")
#
# progress = load_progress()
#
# # page = 1
#
# MAX_PAGES = 2
#
# try:
#     # 1. Выбираем рубрику для тестирования
#     rubric = next(
#         r for r in rubrics
#         if r["name"] == "Рестораны"
#     )
#
#     # 2. Загружаем сохранённый прогресс
#     progress = load_progress()
#
#     page = 1
#
#     if progress and progress["rubric_id"] == str(rubric["id"]):
#         page = progress["page"]
#
#     print(f"📂 Сохранённый прогресс: {progress}")
#     print(f"📄 Требуется продолжить со страницы: {page}")
#
#     # 3. Открываем рубрику
#     url = build_rubric_url(rubric["id"])
#
#     print(f"Обрабатываем рубрику: {rubric['name']}")
#     print(f"URL: {url}")
#
#     driver.get(url)
#     time.sleep(7)
#
#     # 4. Переходим к сохранённой странице
#     for current_page in range(1, page):
#         print(
#             f"➡️ Переход со страницы "
#             f"{current_page} на {current_page + 1}"
#         )
#
#         scroll_until_end(driver)
#
#         if not go_to_next_page(driver):
#             raise RuntimeError(
#                 f"Не удалось перейти на страницу {current_page + 1}"
#             )
#
#     print(f"✅ Открыта страница {page}")
#
#     # 5. Начинаем обычную обработку страниц
#     while True:
#         scroll_until_end(driver)
#
#         # Дальше оставь существующий код обработки карточек
#
#     # Переходим к странице, сохранённой в progress.json
#     for current_page in range(1, page):
#         print(f"➡️ Переход со страницы {current_page} на {current_page + 1}")
#
#         scroll_until_end(driver)
#
#         if not go_to_next_page(driver):
#             raise RuntimeError(
#                 f"Не удалось перейти на страницу {current_page + 1}"
#             )
#
#     print(f"✅ Открыта страница {page}")
#     while True:
#         # 3. Прокручиваем текущую страницу поиска
#         scroll_until_end(driver)
#
#         # 4. Получаем ссылки на организации
#         card_urls = get_card_urls(driver)
#
#         print(f"\n📄 Страница {page}")
#         print(f"Карточек после скролла: {len(get_cards(driver))}")
#         print(f"Получено уникальных ссылок: {len(card_urls)}")
#
#         # Сохраняем адрес поисковой выдачи
#         search_url = driver.current_url
#
#         # 5. Обрабатываем организации
#         for i, url in enumerate(card_urls, start=1):
#             print(f"Обрабатываем {i}/{len(card_urls)}")
#             firm_id = url.rstrip("/").split("/")[-1]
#
#             if firm_id in seen_ids:
#                 print(f"⏭️ Организация {firm_id} уже сохранена. Пропускаем.")
#                 continue
#
#             try:
#                 driver.get(url)
#                 data = parse_card(driver)
#
#                 if not data or data.get("id") is None:
#                     print("⚠️ Не удалось получить ID организации")
#                     continue
#
#                 if data["id"] in seen_ids:
#                     print(f"⚠️ Повторная организация: {data['id']}")
#                     continue
#
#                 append_organization("2gis_data.csv", data)
#
#                 seen_ids.add(data["id"])
#                 results.append(data)
#
#                 print(f"💾 Организация {data['id']} сохранена")
#
#             except Exception as e:
#                 print(f"⚠️ Ошибка обработки {url}: {e}")
#
#         # 6. Сохраняем накопленные результаты
#         # if results:
#         #     with open(
#         #         "2gis_data.csv",
#         #         "w",
#         #         newline="",
#         #         encoding="utf-8"
#         #     ) as f:
#         #         writer = csv.DictWriter(
#         #             f,
#         #             fieldnames=results[0].keys()
#         #         )
#         #         writer.writeheader()
#         #         writer.writerows(results)
#
#             print(f"💾 Сохранено организаций: {len(results)}")
#
#         # Сохраняем следующую страницу для обработки
#         save_progress(rubric["id"], page + 1)
#
#         print(
#             f"💾 Прогресс сохранён: "
#             f"рубрика {rubric['id']}, "
#             f"следующая страница {page + 1}"
#         )
#         # 7. Проверяем лимит страниц
#         if page >= MAX_PAGES:
#             print(f"✅ Достигнут лимит: {MAX_PAGES} страниц")
#             break
#
#         # 8. Возвращаемся к поисковой выдаче
#         driver.get(search_url)
#
#         print("Сохранённый URL поиска:", search_url)
#         print("Текущий URL браузера:", driver.current_url)
#         print("Заголовок страницы:", driver.title)
#         print("Количество карточек:", len(get_cards(driver)))
#
#         # 9. Прокручиваем выдачу для доступа к пагинации
#         scroll_until_end(driver)
#
#         # 10. Переходим на следующую страницу
#         if not go_to_next_page(driver):
#             print("⚠️ Не удалось перейти на следующую страницу")
#             break
#
#         page += 1
#
# finally:
#     print("CSV сохраняется в:", os.path.abspath("2gis_data.csv"))
#     print(f"Всего собрано организаций: {len(results)}")
#     print("Количество уникальных ID:", len(seen_ids))
#     driver.quit()































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