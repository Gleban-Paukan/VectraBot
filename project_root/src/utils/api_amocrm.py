import requests
import src.utils.config as config

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

access_token = config.access_token()
base_url = 'https://vektra.amocrm.ru'
status_id = 67666189

headers = {
    'Authorization': f'Bearer {access_token}',
    'Content-Type': 'application/json'
}


def get_custom_fields(entity_type):
    url = f'{base_url}/api/v4/{entity_type}/custom_fields'

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

def create_lead(city, phone, work_types, work_radius, points, name):
    url = f'{base_url}/api/v4/leads'

    data = [{
        "name": name,
        "status_id": status_id,
        "custom_fields_values": [
            # {
            #     "field_id": _dicts_with_ids["телефон"],
            #     "field_name": "телефон",
            #     "values": [{"value": phone}]
            # },
            {
                "field_id": _dicts_with_ids["Виды работ"],
                "field_name": "Виды работ",
                "values": [{"value": work_types}]
            },
            {
                "field_id": _dicts_with_ids["Радиус работы, км:"],
                "field_name": "Радиус работы, км:",
                "values": [{"value": str(work_radius)}]
            },
            {
                "field_id": _dicts_with_ids["Количество баллов"],
                "field_name": "Количество баллов",
                "values": [{"value": str(points)}]
            },
            {
                "field_id": _dicts_with_ids["Город:"],
                "field_name": "Город:",
                "values": [{"value": city}]
            }
        ]
    }
    ]
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
    url = f'{base_url}/api/v4/leads/{lead_id}'

    data = {
        "custom_fields_values": []
    }

    if fio_birthday is not None:
        data["custom_fields_values"].append({
            "field_id": 980160,
            "field_name": "ФИО+Год рождения",
            "values": [{"value": fio_birthday}]
        })

    if experience is not None:
        data["custom_fields_values"].append({
            "field_id": 980162,
            "field_name": "Опыт работы",
            "values": [{"value": experience}]
        })

    if geo is not None:
        data["custom_fields_values"].append({
            "field_id": 980166,
            "field_name": "Гео",
            "values": [{"value": geo}]
        })

    if history is not None:
        data["custom_fields_values"].append({
            "field_id": 980168,
            "field_name": "История",
            "values": [{"value": history}]
        })

    if example_work is not None:
        data["custom_fields_values"].append({
            "field_id": 980172,
            "field_name": "Пример проф. деятельности",
            "values": [{"value": example_work}]
        })

    if plus_minus is not None:
        data["custom_fields_values"].append({
            "field_id": 980174,
            "field_name": "+ и - Вектры",
            "values": [{"value": plus_minus}]
        })

    if photo is not None:
        data["custom_fields_values"].append({
            "field_id": 980176,
            "field_name": "Фото",
            "values": [{"value": photo}]
        })

    if portfolio is not None:
        data["custom_fields_values"].append({
            "field_id": 980178,
            "field_name": "Портфолио",
            "values": [{"value": portfolio}]
        })
    if average_price is not None:
        data["custom_fields_values"].append({
            "field_id": 982608,
            "field_name": "Средняя стоимость за м2",
            "values": [{"value": str(average_price)}]
        })
    if email is not None:
        data["custom_fields_values"].append({
            "field_id": 982610,
            "field_name": "Email",
            "values": [{"value": email}]
        })
    if site is not None:
        data["custom_fields_values"].append({
            "field_id": 982612,
            "field_name": "Сайт",
            "values": [{"value": site}]
        })

    if not data["custom_fields_values"]:
        print("Нет данных для обновления.")
        return

    response = requests.patch(url, headers=headers, json=data)

    if not (response.status_code in [200, 201]):
        print(f'Ошибка при обновлении лида: {response.status_code}, {response.text}')


def create_contact(name, job_name, geography, average_price_per_m2):
    data = [{
        "name": name,
        "tags": "Монтажник",
        "custom_fields_values": [
            {
                "field_id": 982602,
                "values": [{"value": job_name}]
            },
            {
                "field_id": 982766,
                "values": [{"value": geography}]
            },
            {
                "field_id": 982768,
                "values": [{"value": str(average_price_per_m2)}]
            }
        ]
    }
]
    response = requests.post(f'{base_url}/api/v4/contacts', headers=headers, json=data)

    if response.status_code in [200, 201]:
        contact_id = response.json()['_embedded']['contacts'][0]['id']
        # print(f'Контакт успешно создан с ID: {contact_id}')
        return contact_id
    else:
        print(f'Ошибка при создании контакта: {response.status_code}')
        print('Ответ API:', response.text)
        return None


def attach_contact_to_lead(lead_id, contact_id):
    data = [
        {
            "to_entity_id": int(contact_id),
            "to_entity_type": "contacts"
        }
    ]

    response = requests.post(f'{base_url}/api/v4/leads/{lead_id}/link', headers=headers, json=data)

    if response.status_code in [200, 204, 201]:
        print(f'Контакт с ID {contact_id} успешно привязан к лиду с ID {lead_id}.')
        return True
    else:
        print(f'Ошибка при привязке контакта к лиду: {response.status_code}')
        print('Ответ API:', response.text)
        return False
