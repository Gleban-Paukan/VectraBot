import sqlite3
from datetime import datetime
import json


def get_connection():
    return sqlite3.connect('general_data_base.db')


class SQLiteUser:
    id = int

    def __init__(self, user_id: int, user_name: str = None):
        with get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM User WHERE user_id = ?', (user_id,))
            current_user = cursor.fetchone()
            if current_user:
                self.user_id = user_id
            else:
                cursor.execute(
                    'INSERT INTO User (user_id, username, develop_project_documentation, earthworks, '
                    'puring_the_foundation, manufacture_metal_structures, installation_metal_structures, '
                    'installation_sandwich_panels, interior_decoration, installation_windows) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_id, user_name, 0, 0, 0, 0, 0, 1, 0, 0)
                )
                self.id = user_id

    def __getattribute__(self, name):
        with get_connection() as conn:
            cursor = conn.cursor()
            if name == "user_id" or name.startswith("__") or name in dir(self):
                return object.__getattribute__(self, name)
            cursor.execute(f'SELECT {name} FROM User WHERE user_id = ?', (self.user_id,))
            result = cursor.fetchone()
            if result is not None:
                return result[0]
            else:
                raise AttributeError(f"Attribute '{name}' not found")

    def add_job_option(self, job_name: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE User SET {job_name} = 1 WHERE user_id = ?', (self.user_id,))

    def remove_job_option(self, job_name: str):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE User SET {job_name} = 0 WHERE user_id = ?', (self.user_id,))

    def change_city(self, city_name):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET city_name = ? WHERE user_id = ?', (city_name, self.user_id))

    def change_position(self, latitude, longitude):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET latitude = ?, longitude = ?  WHERE user_id = ?',
                           (latitude, longitude, self.user_id))

    def change_radius(self, radius):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET radius = ? WHERE user_id = ?', (radius, self.user_id))

    def change_phone_number(self, phone_number):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET phone_number = ? WHERE user_id = ?', (phone_number, self.user_id))

    def change_balance(self, balance):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET balance = ? WHERE user_id = ?', (balance, self.user_id))

    def change_manager(self, manager_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET manager = ? WHERE user_id = ?', (manager_id, self.user_id))

    def change_object_description(self, object_description):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET object_description = ? WHERE user_id = ?',
                           (object_description, self.user_id))

    def change_types_of_completed_works(self, types_of_completed_works):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET types_of_completed_works = ? WHERE user_id = ?',
                           (types_of_completed_works, self.user_id))

    def change_average_price(self, average_price):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET average_price = ? WHERE user_id = ?', (average_price, self.user_id))

    def change_path_to_images(self, path_to_images):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET path_to_images = ? WHERE user_id = ?',
                           (path_to_images, self.user_id))

    def change_email(self, email):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET email = ? WHERE user_id = ?',
                           (email, self.user_id))


def check_radius_exists(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT radius FROM User WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

    if result and result[0] is not None:
        return True
    else:
        return False
