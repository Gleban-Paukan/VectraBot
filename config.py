import data_base_functions
import Levenshtein
import sqlite3
import re

jobs_dict = {
    "develop_project_documentation": "Разработка проектной документации",
    "earthworks": "Земляные работы",
    "puring_the_foundation": "Заливка фундамента / монолитной плиты",
    "manufacture_metal_structures": "Изготовление металлоконструкций",
    "installation_metal_structures": "Монтаж металлоконструкций",
    "installation_sandwich_panels": "Монтаж сэндвич-панелей",
    "interior_decoration": "Внутренняя отделка и инженерные системы",
    "installation_windows": "Установка окон / дверей"
}
job_to_variable = {
    "Разработка проектной документации": "develop_project_documentation",
    "Земляные работы": "earthworks",
    "Заливка фундамента / монолитной плиты": "puring_the_foundation",
    "Изготовление металлоконструкций": "manufacture_metal_structures",
    "Монтаж металлоконструкций": "installation_metal_structures",
    "Монтаж сэндвич-панелей": "installation_sandwich_panels",
    "Внутренняя отделка и инженерные системы": "interior_decoration",
    "Установка окон / дверей": "installation_windows",

    "✅ Разработка проектной документации": "develop_project_documentation",
    "✅ Земляные работы": "earthworks",
    "✅ Заливка фундамента / монолитной плиты": "puring_the_foundation",
    "✅ Изготовление металлоконструкций": "manufacture_metal_structures",
    "✅ Монтаж металлоконструкций": "installation_metal_structures",
    "✅ Монтаж сэндвич-панелей": "installation_sandwich_panels",
    "✅ Внутренняя отделка и инженерные системы": "interior_decoration",
    "✅ Установка окон / дверей": "installation_windows"
}


def first_bot_token():
    return "7013658952:AAH1TSd2Mffq_GAj6z_rC2am9kgBQVWNeoY"


def id_of_chat_vectra_montajniki():
    return -4230923765


def define_list_of_jobs(user_id: int):
    user = data_base_functions.SQLiteUser(user_id)
    list_of_jobs = []
    for i in jobs_dict:
        if user.__getattribute__(i):
            list_of_jobs.append(f"✅ {jobs_dict[i]}")
        else:
            list_of_jobs.append(f"{jobs_dict[i]}")
    return list_of_jobs


def define_list_of_jobs_only_useful(user_id: int):
    user = data_base_functions.SQLiteUser(user_id)
    list_of_jobs = []
    for i in jobs_dict:
        if user.__getattribute__(i):
            list_of_jobs.append(f"{jobs_dict[i]}")
    return list_of_jobs


def find_similar_cities(city_name: str, max_distance: int = 1):
    connection = sqlite3.connect('cities.db')
    cursor = connection.cursor()
    cursor.execute('SELECT city_name FROM cities')
    cities = cursor.fetchall()
    connection.close()

    similar_cities = []
    for (city,) in cities:
        distance = Levenshtein.distance(city_name.lower(), city.lower())
        if distance <= max_distance:
            similar_cities.append(city)

    return similar_cities


def is_valid_phone_number(phone_number):
    pattern = r'^\+7\d{10}$'
    return re.match(pattern, phone_number) is not None
