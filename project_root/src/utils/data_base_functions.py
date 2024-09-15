import sqlite3
import src.utils.config as config


def get_connection():
    return sqlite3.connect(config.path_to_general_data_base())


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
                    'installation_sandwich_panels, interior_decoration, installation_windows, turnkey_work) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    (user_id, user_name, 0, 0, 0, 0, 0, 1, 0, 0, 0)
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

    def change_path_to_portfolio(self, path_to_portfolio):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET path_to_portfolio = ? WHERE user_id = ?',
                           (path_to_portfolio, self.user_id))

    def change_email(self, email):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET email = ? WHERE user_id = ?',
                           (email, self.user_id))

    def change_lead_id(self, lead_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET lead_id = ? WHERE user_id = ?',
                           (lead_id, self.user_id))

    def change_contact_id(self, contact_id):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET contact_id = ? WHERE user_id = ?',
                           (contact_id, self.user_id))

    def change_site(self, site):
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET site = ? WHERE user_id = ?',
                           (site, self.user_id))

    def add_order(self, order_id):
        order_id = str(order_id) + " " + (self.orders_id if self.orders_id else "")
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE User SET orders_id = ? WHERE user_id = ?',
                           (order_id, self.user_id))

    def define_check_mark(self, attr):
        return "✅" if self.__getattribute__(attr) is not None else ""


def add_admin_id(user_id: int):
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM Admin WHERE user_id = ?', (user_id,))
        current_user = cursor.fetchone()
        if not current_user:
            cursor.execute(
                'INSERT INTO Admin (user_id) '
                'VALUES (?)',
                (user_id,)
            )


def get_ids_for_order_notification(city):
    query = """
SELECT user_id 
FROM User 
WHERE city_name != ''  -- Проверяем, что список городов не пуст
  AND (((' ' || city_name || ' ') LIKE ('% ' || ? || ' %'))  -- Проверяем наличие заданного города
       OR ((' ' || city_name || ' ') LIKE ('% Россия %')));  -- Проверяем наличие "Россия" в списке городов
"""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (city,))
        results = cursor.fetchall()
        return results


def change_order_status(order_id, new_status):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE "Order" SET status = ? WHERE order_id = ?',
                       (new_status, order_id))


def get_admins_list():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Admin")
        results = cursor.fetchall()
        return results


def get_order_data(message_id):
    query = f"""
SELECT order_id, square, city, jobs, address, status
FROM "Order" 
WHERE order_id == (?)
"""

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (message_id,))
        results = cursor.fetchall()
        return results


def add_order(order_id, square, city, jobs, address):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO "Order" (order_id, square, city, jobs, address, status)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    try:
        cursor.execute(query, (order_id, square, city, jobs, address, "WAITING"))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении данных: {e}")
    finally:
        conn.close()


def check_radius_exists(user_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT radius FROM User WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()

    if result and result[0] is not None:
        return True
    else:
        return False
