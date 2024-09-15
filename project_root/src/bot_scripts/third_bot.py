import sys
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from telebot import types
from requests import ReadTimeout
import os

import src.utils.data_base_functions as data_base_functions
import src.utils.config as config

bot = telebot.TeleBot(config.third_bot_token())
second_bot = telebot.TeleBot(config.second_bot_token())
second_bot.parse_mode = 'html'
bot.parse_mode = 'html'

jobstores = {
    'default': SQLAlchemyJobStore(url=config.path_to_jobsDB())
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()

users_data_to_post = {}
jobs_kinds = {
    1: "Разработка проектной документации",
    2: "Земляные работы",
    3: "Заливка фундамента / монолитной плиты",
    4: "Изготовление металлоконструкций",
    5: "Монтаж металлоконструкций",
    6: "Монтаж сэндвич-панелей",
    7: "Внутренняя отделка и инженерные системы",
    8: "Установка окон / дверей"
}


@bot.callback_query_handler(func=lambda call: True)
def inline_handler(call):
    if "confirm_order" in call.data:
        executor_id = int(call.data.split("+/+")[1])
        order_id = int(call.data.split("+/+")[2])
        order_data = data_base_functions.get_order_data(order_id)[0]
        square = order_data[1]
        city = order_data[2]
        jobs = order_data[3].split(",")
        address = order_data[4]
        text = f"""
Информация по заказу:
    
🔨Виды работ:
<b>
{'\n'.join(jobs)}
</b>
📍Объект по адресу: <b>{city}, {address}</b>
📏Объем: {square} м²           
            """
        data_base_functions.change_order_status(order_id, "IN_WORK")
        bot.send_message(call.message.chat.id, "Заказ взят в работу!")
        second_bot.send_message(executor_id, f"Вас выбрали исполнителем в заказе №{order_id}\n\n" + text)


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    data_base_functions.add_admin_id(message.chat.id)
    bot.send_message(message.chat.id, "Привет! Это бот размещения заказов в закрытом клубе <b>«МОНТАЖНИКИ ВЕКТРА»</b>"
                                      "\n\nДля того, чтобы разместить заказ на монтаж, заполните данные:")
    bot.send_message(message.chat.id, "Укажите только город.")
    bot.register_next_step_handler(message, register_city)


def register_city(msg):
    users_data_to_post[msg.chat.id] = {"city": msg.text, "square": 0.0, "jobs": "", "address": ""}
    bot.send_message(msg.chat.id, "Напишите адрес. Например: улица Академика Павлова, 35 ")
    bot.register_next_step_handler(msg, register_address)


def register_address(msg):
    users_data_to_post[msg.chat.id]["address"] = msg.text
    bot.send_message(msg.chat.id, "Укажите <b>объем объекта в м²</b>")
    bot.register_next_step_handler(msg, register_square)


def register_square(msg):
    if msg.text.isdigit():
        users_data_to_post[msg.chat.id]["square"] = float(msg.text)
        text = """
<b>Укажите виды работ, которые необходимо выполнить:</b>

1. Разработка проектной документации
2. Земляные работы
3. Заливка фундамента / монолитной плиты
4. Изготовление металлоконструкций
5. Монтаж металлоконструкций
6. Монтаж сэндвич-панелей
7. Внутренняя отделка и инженерные системы
8. Установка окон / дверей\n\n
"""
        bot.send_message(msg.chat.id, text + "Укажите последовательность чисел через пробел.\nEx: 2 5 3")
        bot.register_next_step_handler(msg, register_jobs)
    else:
        bot.send_message(msg.chat.id, "Введите только число. Попробуйте еще раз")
        bot.register_next_step_handler(msg, register_square)


def register_jobs(msg):
    list_of_jobs_numbers = msg.text.split()
    if all(num.isdigit() for num in list_of_jobs_numbers):
        if any((int(num) >= 9 or int(num) <= 0) for num in list_of_jobs_numbers):
            bot.send_message(msg.chat.id, "Укажите только последовательность чисел, через пробел, Пример: 2 5 1.")
            bot.register_next_step_handler(msg, register_jobs)
            return
        users_data_to_post[msg.chat.id]["jobs"] = msg.text
        text = f"""
Виды работ:
<b>
{'\n'.join([jobs_kinds[int(i)] for i in list_of_jobs_numbers])}
</b>
Объект по адресу: {users_data_to_post[msg.chat.id]['city']}, {users_data_to_post[msg.chat.id]['address']}
Объем: {users_data_to_post[msg.chat.id]['square']} м^2
Адрес: {users_data_to_post[msg.chat.id]['address']}

Всё верно?
"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Да, всё верно!"), types.KeyboardButton("Нет, заполнить заново!"))
        bot.send_message(msg.chat.id, text, reply_markup=markup)
        return

    bot.send_message(msg.chat.id, "Укажите только последовательность чисел, через пробел, Пример: 2 5 3.")
    bot.register_next_step_handler(msg, register_jobs)


@bot.message_handler(content_types=['text'])
def text_message_handler(message):
    if message.text == "Да, всё верно!":
        text = f"""
Я подобрала вам клиента!
На связи виртуальный ассистент клуба — Вира👷🏼‍♀️

Заявка на 
<b>
—{'\n—'.join([jobs_kinds[int(i)] for i in users_data_to_post[message.chat.id]["jobs"].split()])}
</b>

Объект по адресу: {users_data_to_post[message.chat.id]['city']}, {users_data_to_post[message.chat.id]['address']}
Объем: {users_data_to_post[message.chat.id]['square']}
"""
        text_for_chat = f"""
На связи виртуальный ассистент клуба — Вира👷🏼‍♀️

Заявка на 
<b>
—{'\n—'.join([jobs_kinds[int(i)] for i in users_data_to_post[message.chat.id]["jobs"].split()])}
</b>

Объект по адресу: {users_data_to_post[message.chat.id]['city']}, {users_data_to_post[message.chat.id]['address']}
Объем: {users_data_to_post[message.chat.id]['square']}
"""
        markup_for_chat = types.InlineKeyboardMarkup(row_width=1)
        markup_for_chat.add(types.InlineKeyboardButton("Взять заказ ✅",
                                                       url=f"https://t.me/vektra_installation_club_bot?start=order_{message.id}"))
        second_bot.send_message(config.id_of_chat_vectra_montajniki(), text_for_chat, reply_markup=markup_for_chat)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Взять заказ ✅", callback_data=f"order+/+{message.id}"))
        data_base_functions.add_order(message.id, city=users_data_to_post[message.chat.id]['city'],
                                      square=users_data_to_post[message.chat.id]['square'], jobs=','.join(
                [jobs_kinds[int(i)] for i in users_data_to_post[message.chat.id]["jobs"].split()]),
                                      address=users_data_to_post[message.chat.id]['address'])
        for user_id in data_base_functions.get_ids_for_order_notification(users_data_to_post[message.chat.id]["city"]):
            print(user_id)
            second_bot.send_message(user_id[0], text, reply_markup=markup)
    if message.text == "Нет, заполнить заново!":
        bot.send_message(message.chat.id, "Укажите город и область, в котором планируется выполнять работы")
        bot.register_next_step_handler(message, register_city)
    if "/finish" in message.text:
        order_id = message.text.split("_")
        data_base_functions.change_order_status(order_id, "COMPLETE")
        bot.send_message(message.chat.id, f"Заказ {order_id} теперь завершён!")


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
