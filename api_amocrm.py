import requests

email = 'marketing@vektragroup.ru'

_dicts_with_ids = {
    "Виды работ": 982140,
    "Радиус работы, км:": 982142,
    "Количество баллов": 982146,
    "телефон": 412731,
    "Город:": 982144,
    "Email": email,
    "Сайт": 470421
}

access_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjNjMmQxODU5NjMwYWY0N2VjNDgyYzllNzFmMGZmN2I1NDNmYWNkNWU3MDAzYTJkYjU1ZmNhZDgyMTI3N2U0YmNkOWFhMjhhOTA4ZGVhNDQ4In0.eyJhdWQiOiIxOWM3NzE0OS1iODBhLTRiNDktODhhMS1lNDAwZjNmNzBiYWMiLCJqdGkiOiIzYzJkMTg1OTYzMGFmNDdlYzQ4MmM5ZTcxZjBmZjdiNTQzZmFjZDVlNzAwM2EyZGI1NWZjYWQ4MjEyNzdlNGJjZDlhYTI4YTkwOGRlYTQ0OCIsImlhdCI6MTcyNjA2NDI4MSwibmJmIjoxNzI2MDY0MjgxLCJleHAiOjE3NjcyMjU2MDAsInN1YiI6IjExMzEwODk3IiwiZ3JhbnRfdHlwZSI6IiIsImFjY291bnRfaWQiOjE3NjMwNTI3LCJiYXNlX2RvbWFpbiI6ImFtb2NybS5ydSIsInZlcnNpb24iOjIsInNjb3BlcyI6WyJjcm0iLCJmaWxlcyIsImZpbGVzX2RlbGV0ZSIsIm5vdGlmaWNhdGlvbnMiLCJwdXNoX25vdGlmaWNhdGlvbnMiXSwiaGFzaF91dWlkIjoiYjBiM2JlYzAtZTQ4Mi00NDlkLWJkYWQtNDdhYWIwODVjZGQ1IiwiYXBpX2RvbWFpbiI6ImFwaS1hLmFtb2NybS5ydSJ9.qOIQTjZxkiOXEZwVR-2znznFoj_BDyIS_c4qQxOPTHwuTolFN0ZlgGGUeUn2Fpbif0L_dlHRbAmgkYWjTRTlwe_DVDsQ6hs-Nr6Zg76WEJkRK3FjUlTMwEOK0DJYc0wVuhsW11WzV2RSPia_hC-Sbb0fBIs0vM39jmpilXOx2nypWbatJEoJ-zjHpuyiZHuDC66vGBl-pZCIrok8uNJr3xyogjfv22t5wV2hUk9pYKDZGK1cakpU9IPaZJzKAqn4gAbPd3yFEoDhH3YsJRhpISYiX7s4dGH6mmIvqKGxlDKAXPWPwmoB5Zg_yizJbSItRKbUk9hZTUgTIqM4PsmWuA'  # Замените на ваш актуальный access_token
base_url = 'https://vektra.amocrm.ru'  # Замените на ваш домен в amoCRM
# ID статуса, в который должен попадать лид
status_id = 67666189


# Контактная почта для уведомлений или использования

# Функция для получения всех пользовательских полей сущности
def get_custom_fields(entity_type):
    url = f'{base_url}/api/v4/{entity_type}/custom_fields'  # Эндпоинт для пользовательских полей

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        fields_data = response.json()
        custom_fields = fields_data.get('_embedded', {}).get('custom_fields', [])

        # Выводим название и ID каждого пользовательского поля
        for field in custom_fields:
            print(f"Название: {field['name']}, ID: {field['id']}")

        return custom_fields
    else:
        print(f'Ошибка при получении пользовательских полей для {entity_type}: {response.status_code}, {response.text}')
        return None


# Получение пользовательских полей для каждой сущности
# print("Пользовательские поля для Контактов:")
# custom_fields_contacts = get_custom_fields('contacts')
#
# print("\nПользовательские поля для Сделок:")
# custom_fields_leads = get_custom_fields('leads')
#

#
# print("\nПользовательские поля для Компаний:")
# custom_fields_companies = get_custom_fields('companies')
#
# print("\nПользовательские поля для Задач:")
# custom_fields_tasks = get_custom_fields('tasks')
# Функция для создания лида
def create_lead(city, phone, work_types, work_radius, points, name):
    url = f'{base_url}/api/v4/leads'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Данные для создания лида
    data = [{
        "name": name,  # Название лида, обычно указывают имя клиента или другую информацию
        "status_id": status_id,  # ID статуса, в который должен попадать лид
        "custom_fields_values": [
            # {
            #     "field_id": _dicts_with_ids["телефон"],  # Замените на фактический ID поля "Виды работ"
            #     "field_name": "телефон",
            #     "values": [{"value": phone}]
            # },
            {
                "field_id": _dicts_with_ids["Виды работ"],  # Замените на фактический ID поля "Виды работ"
                "field_name": "Виды работ",
                "values": [{"value": work_types}]
            },
            {
                "field_id": _dicts_with_ids["Радиус работы, км:"],  # Замените на фактический ID поля "Радиус работ"
                "field_name": "Радиус работы, км:",
                "values": [{"value": str(work_radius)}]
            },
            {
                "field_id": _dicts_with_ids["Количество баллов"],  # Замените на фактический ID поля "Количество баллов"
                "field_name": "Количество баллов",
                "values": [{"value": str(points)}]
            },
            {
                "field_id": _dicts_with_ids["Город:"],  # Замените на фактический ID поля "Количество баллов"
                "field_name": "Город:",
                "values": [{"value": city}]
            }
        ]
    }
    ]
    # Выполнение POST-запроса для создания лида
    response = requests.post(url, headers=headers, json=data)

    if response.status_code in [201, 200]:
        lead_data = response.json()
        lead_id = lead_data['_embedded']['leads'][0]['id']
        return lead_id
    else:
        print(f'Ошибка при создании лида: {response.status_code}, {response.text}')
        return None


def update_lead_fields(lead_id, experience=None, example_work=None, photo=None, portfolio=None,
                       fio_birthday=None, geo=None, plus_minus=None, history=None, average_price=None, email=None,
                       site=None):
    url = f'{base_url}/api/v4/leads/{lead_id}'  # Эндпоинт для обновления лида

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Создаем массив данных для обновления
    data = {
        "custom_fields_values": []
    }

    # Добавляем поля только если их значения не None
    if fio_birthday is not None:
        data["custom_fields_values"].append({
            "field_id": 980160,  # ID поля "ФИО+Год рождения"
            "field_name": "ФИО+Год рождения",
            "values": [{"value": fio_birthday}]
        })

    if experience is not None:
        data["custom_fields_values"].append({
            "field_id": 980162,  # ID поля "Опыт работы"
            "field_name": "Опыт работы",
            "values": [{"value": experience}]
        })

    if geo is not None:
        data["custom_fields_values"].append({
            "field_id": 980166,  # ID поля "Гео"
            "field_name": "Гео",
            "values": [{"value": geo}]
        })

    if history is not None:
        data["custom_fields_values"].append({
            "field_id": 980168,  # ID поля "История"
            "field_name": "История",
            "values": [{"value": history}]
        })

    if example_work is not None:
        data["custom_fields_values"].append({
            "field_id": 980172,  # ID поля "Пример проф. деятельности"
            "field_name": "Пример проф. деятельности",
            "values": [{"value": example_work}]
        })

    if plus_minus is not None:
        data["custom_fields_values"].append({
            "field_id": 980174,  # ID поля "+ и - Вектры"
            "field_name": "+ и - Вектры",
            "values": [{"value": plus_minus}]
        })

    if photo is not None:
        data["custom_fields_values"].append({
            "field_id": 980176,  # ID поля "Фото"
            "field_name": "Фото",
            "values": [{"value": photo}]
        })

    if portfolio is not None:
        data["custom_fields_values"].append({
            "field_id": 980178,  # ID поля "Портфолио"
            "field_name": "Портфолио",
            "values": [{"value": portfolio}]
        })
    if average_price is not None:
        data["custom_fields_values"].append({
            "field_id": 982608,  # ID поля "Портфолио"
            "field_name": "Средняя стоимость за м2",
            "values": [{"value": str(average_price)}]
        })
    if email is not None:
        data["custom_fields_values"].append({
            "field_id": 982610,  # ID поля "Портфолио"
            "field_name": "Email",
            "values": [{"value": email}]
        })
    if site is not None:
        data["custom_fields_values"].append({
            "field_id": 982612,  # ID поля "Портфолио"
            "field_name": "Сайт",
            "values": [{"value": site}]
        })

    # Проверяем, есть ли что-то для обновления
    if not data["custom_fields_values"]:
        print("Нет данных для обновления.")
        return

    # Выполнение PATCH-запроса для обновления лида
    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f'Лид с ID {lead_id} успешно обновлен.')
    else:
        print(f'Ошибка при обновлении лида: {response.status_code}, {response.text}')
