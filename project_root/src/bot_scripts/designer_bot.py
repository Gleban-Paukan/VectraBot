import telebot
import src.utils.api_amocrm as api_amocrm
import src.utils.data_base_functions as data_base_functions
from requests import ReadTimeout
import os
import sys

import src.utils.config as config

bot = telebot.TeleBot(config.designer_bot_token())
second_bot = telebot.TeleBot(config.second_bot_token())
PORTFOLIO_DIR = '/home/vectra_telegram_bot/project_root/user_data/user_portfolios'  # ../../user_data/user_portfolios

if not os.path.exists(PORTFOLIO_DIR):
    os.makedirs(PORTFOLIO_DIR)


@bot.message_handler(commands=['start'])
def start_command(message):
    bot.send_message(message.chat.id,
                     "Привет! Я буду присылать заявки на дизайн. Когда придет заявка с данными, "
                     "просто нажми на кнопку 'Отправить портфолио' и пришли pdf файл.")


@bot.callback_query_handler(func=lambda call: "request_pdf" in call.data)
def handle_pdf_request(call):
    msg = bot.send_message(call.message.chat.id, "Пожалуйста, отправьте мне PDF файл.")
    bot.register_next_step_handler(msg, handle_document, call.data.split("_")[2])


def handle_document(message, user_id):
    print(user_id)
    if message.document.mime_type == 'application/pdf':
        try:
            user = data_base_functions.SQLiteUser(user_id)
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(f"{PORTFOLIO_DIR}/{message.document.file_name}", 'wb') as new_file:
                new_file.write(downloaded_file)
            user.change_path_to_portfolio(f"{PORTFOLIO_DIR}/{message.document.file_name}")
            if user.contact_id is None:
                contact_id = api_amocrm.create_contact(name=message.chat.id, geography=user.city_name,
                                                       job_name=", ".join(
                                                           config.define_list_of_jobs_only_useful(user.user_id)),
                                                       average_price_per_m2=user.average_price)
                user.change_contact_id(contact_id)
            api_amocrm.update_lead_fields(user.lead_id, experience=user.types_of_completed_works, geo=user.city_name,
                                          email=user.email,
                                          average_price=user.average_price, site=user.site)
            api_amocrm.attach_contact_to_lead(user.lead_id, user.contact_id)
            bot.send_message(message.chat.id, "Файл успешно загружен!")
            with open(f"{PORTFOLIO_DIR}/{message.document.file_name}", "rb") as file:
                second_bot.send_document(user_id, document=file, caption="Ваше портфолио готово!")
        except Exception as e:
            bot.send_message(message.chat.id, f"Произошла ошибка при загрузке файла: {e}")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, отправьте файл в формате PDF.")


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
