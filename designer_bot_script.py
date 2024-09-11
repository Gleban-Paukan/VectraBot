import telebot
from telebot import types
import api_amocrm
import data_base_functions
from requests import ReadTimeout
import os
import sys

import config

# Ваш токен API Telegram

bot = telebot.TeleBot(config.designer_bot_token())
second_bot = telebot.TeleBot(config.second_bot_token())
PORTFOLIO_DIR = 'user_portfolios'

if not os.path.exists(PORTFOLIO_DIR):
    os.makedirs(PORTFOLIO_DIR)


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,
                     "Привет! Я буду присылать заявки на дизайн. Когда придет заявка с данными, "
                     "просто нажми на кнопку 'Отправить портфолио' и пришли pdf файл.")


# Обработчик нажатия кнопки
@bot.callback_query_handler(func=lambda call: "request_pdf" in call.data)
def handle_pdf_request(call):
    msg = bot.send_message(call.message.chat.id, "Пожалуйста, отправьте мне PDF файл.")
    bot.register_next_step_handler(msg, handle_document, call.data.split("_")[2])


# Обработчик получения файла PDF
# @bot.message_handler(content_types=['document'])
def handle_document(message, user_id):
    print(user_id)
    if message.document.mime_type == 'application/pdf':  # Проверяем, что файл PDF
        try:
            user = data_base_functions.SQLiteUser(user_id)

            # Скачиваем файл
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            # Сохраняем файл локально
            with open(f"{PORTFOLIO_DIR}/{message.document.file_name}", 'wb') as new_file:
                new_file.write(downloaded_file)
            user.change_path_to_portfolio(f"{PORTFOLIO_DIR}/{message.document.file_name}")
            api_amocrm.update_lead_fields(user.lead_id, experience=user.types_of_completed_works, geo=(
                f"Широта: {user.latitude}, Долгота: {user.longitude}, Радиус работы: "
                f"{user.radius}" if user.longitude is not None else "Вся Россия"), email=user.email,
                                          average_price=user.average_price, site=user.site)
            # Отправляем сообщение об успехе
            bot.send_message(message.chat.id, "Файл успешно загружен!")
            with open(f"{PORTFOLIO_DIR}/{message.document.file_name}", "rb") as file:
                second_bot.send_document(user_id, document=file, caption="Ваше портфолио готово!")
        except Exception as e:
            # Отправляем сообщение об ошибке
            bot.send_message(message.chat.id, f"Произошла ошибка при загрузке файла: {e}")
    else:
        # Отправляем сообщение, если файл не PDF
        bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате PDF.")


# Запуск бота
if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
