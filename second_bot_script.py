import time
import sys
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
from telebot import types
from requests import ReadTimeout
import os

from telebot.types import ForceReply

import data_base_functions
import config
import text_messages_storage

PHOTO_DIR = 'user_photos'

if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

bot = telebot.TeleBot(config.second_bot_token())
bot.parse_mode = 'html'

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    user_id = message.chat.id  # TODO REMOVE JOB OF REGISTRATION REMIND BOT 1
    user = data_base_functions.SQLiteUser(user_id)
    if user.balance is None:
        user.change_balance(1000)
        # scheduler.remove_job(f"{user_id}_city_remind")
        if data_base_functions.check_radius_exists(user_id):
            schedule_reminder(user_id, f"{user_id}_register_confirmation_1_remind_second_bot", 2880,
                              text_messages_storage.message_definer(19))
            schedule_reminder(user_id, f"{user_id}_register_confirmation_2_remind_second_bot", 7200,
                              text_messages_storage.message_definer(17))
            schedule_reminder(user_id, f"{user_id}_register_confirmation_3_remind_second_bot", 1080,
                              text_messages_storage.message_definer(18))
            bot.send_message(user_id, text_messages_storage.message_definer(20),
                             reply_markup=config.start_markup())
            typing_action(user_id, 2)
            bot.send_message(user_id, text_messages_storage.message_definer(12))
            typing_action(user_id, 5)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Как получать заказы на монтаж?", callback_data="wanna_know_more_montage"),
                types.InlineKeyboardButton("Узнать больше о программе лояльности",
                                           callback_data="information_about_referral_program"))  # stupid value name
            bot.send_message(user_id, f'Благодарим вас за регистрацию в профессиональном строительном сообществе '
                                      f'"ВЕКТРА", ваш баланс бонусных баллов составляет: {user.balance}\n\n'
                                      'Выберете, о чем вы хотели бы узнать подробнее', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Возвращено в меню.", reply_markup=config.start_markup())


@bot.message_handler(content_types=['text'])
def text_message_handler(message):
    if message.text == "🎁 Программа лояльности":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Мой баланс", callback_data="get_user_balance"),
                   types.InlineKeyboardButton("Как получить больше баллов",
                                              callback_data="information_about_referral_program"))
        bot.send_message(message.chat.id, "Какая информация Вас интересует?", reply_markup=markup)
    elif message.text == "💬 Техническая поддержка и обратная связь":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Чат-бот", url="https://t.me/mrk_vektra"),
                   types.InlineKeyboardButton("Звонок на квалификатора", callback_data="call_to_qualifier"))
        markup.add(types.InlineKeyboardButton("Популярные вопросы и ответы", callback_data="FAQ"))
        bot.send_message(message.chat.id, "Выберите способ связи:", reply_markup=markup)
    elif message.text == "👤 Мой профиль":
        msg_to_profile(message.chat.id)
    elif message.text == "📝 Рассказать о своем проекте":
        bot.send_message(message.chat.id, "TODO")
    elif message.text == "🏚 Мои заказы":
        bot.send_message(message.chat.id, "TODO")
    elif message.text == "👨‍💼 Мой менеджер":
        user = data_base_functions.SQLiteUser(message.chat.id)
        if user.manager is None:
            schedule_manager(message.chat.id)
            bot.send_message(message.chat.id, "Ваша заявка на подбор принята!")
            bot.send_message(message.chat.id, "Подберем для вас самого лучшего менеджера и обязательно вас познакомим!"
                                              "\n\nОбычно это занимает не более 3 часов ⏰")
            user.change_manager("SEARCHING")
        elif user.manager == "SEARCHING":
            bot.send_message(message.chat.id,
                             "Пока у вас нет личного менеджера, но скоро появится, ваша заявка в работе!")
        else:
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("Связаться в Telegram", url="https://t.me/+79370602463"),
                       types.InlineKeyboardButton("Связаться в WhatsApp", url="https://wa.me/79370602463"))
            bot.send_message(message.chat.id,
                             "Ваш персональный менеджер — <b>Мария</b>.\nКонтактный номер: <b>+79370602463</b>\n"
                             "Электронная почта: <b>m.lukyanova@vektra.online</b>",
                             reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def inline_handler(call):
    deleting_flag = True
    if call.data == "wanna_know_more_montage":
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_1_remind_second_bot")
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_2_remind_second_bot")
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_3_remind_second_bot")
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Да", callback_data="example_message"),
                   types.InlineKeyboardButton("Нет", callback_data="dont_need_example_message"))
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(14))
        bot.send_message(call.message.chat.id, "Хотите посмотреть пример такого сообщения?", reply_markup=markup)
    elif call.data == "example_message":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Взять заказ", callback_data="finish_of_example_message"),
                   types.InlineKeyboardButton("Отказ", callback_data="finish_of_example_message"))
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(21))
        typing_action(call.message.chat.id, 2)
        bot.send_message(call.message.chat.id, "Далее вам необходимо выбрать: возьмете вы заказ или нет.")
        bot.send_message(call.message.chat.id, "Давайте попробуем:", reply_markup=markup)
    elif call.data == "finish_of_example_message":
        bot.send_message(call.message.chat.id, "Отлично, теперь вы знаете, как работает наш чат-бот! Как только у "
                                               "нас появятся актуальные заявки на монтаж, я сразу же сообщу вам об этом."
                                               " Благодарю вас за ожидание и надеюсь на дальнейшее сотрудничество!")
    elif call.data == "information_about_referral_program":
        with open("referral_instructions.png", "rb") as photo:
            bot.send_photo(call.message.chat.id, caption=text_messages_storage.message_definer(8), photo=photo)
        typing_action(call.message.chat.id, 1)
        bot.send_message(call.message.chat.id, "<b>Уже захотелось стать участником программы лояльности? "
                                               "А чтобы окончательно отбросить все ваши сомнения рассказываем об акциях"
                                               " и бонусах в рамках программы: </b>")
        typing_action(call.message.chat.id, 6)
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(11),
                         reply_markup=config.start_markup())
        deleting_flag = False

    elif call.data == "get_user_balance":
        bot.send_message(call.message.chat.id, "TODO", reply_markup=config.start_markup())
    elif call.data == "call_to_qualifier":
        bot.send_message(call.message.chat.id, "TODO", reply_markup=config.start_markup())
    elif call.data == "FAQ":
        bot.send_message(call.message.chat.id, "TODO", reply_markup=config.start_markup())
    elif "toggle+/+" in call.data:
        job_data = call.data.split("+/+")
        job_name = job_data[1]
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        if user.__getattribute__(job_name):
            user.remove_job_option(job_name)
        else:
            user.add_job_option(job_name)
        if len(job_data) == 2:
            markup = define_job_markup(call.message.chat.id)
        else:
            markup = define_job_markup(call.message.chat.id, job_data[2], False)
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=markup)
        deleting_flag = False
    elif "change+/+" in call.data:
        value = call.data.split("+/+")[1]
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("Назад в меню")
        if value == "job_categories":
            markup = define_job_markup(call.message.chat.id, "back_to_profile", False)
            bot.send_message(call.message.chat.id, "Укажите, какие категории хотите добавить или убрать.",
                             reply_markup=markup)
        elif value == "city_name":
            msg = bot.send_message(call.message.chat.id, "Введите новый город:", reply_markup=markup)
            bot.register_next_step_handler(msg, change_city_name)
        elif value == "phone_number":
            msg = bot.send_message(call.message.chat.id, "Введите новый номер телефона в формате +7**********:",
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, change_phone_number)
        elif value == "radius":
            msg = bot.send_message(call.message.chat.id, "Введите целое число: максимальное расстояние, "
                                                         "которое готовы взять в работу.",
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, change_radius)
    elif call.data == "add_additional_information":
        markup = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton("Описание объекта", callback_data="description"),
            types.InlineKeyboardButton("Вид выполненных работ", callback_data="work_type"),
            types.InlineKeyboardButton("Средняя стоимость за м²", callback_data="cost"),
            types.InlineKeyboardButton("Загрузить фотографии", callback_data="upload_photos"),
            types.InlineKeyboardButton("Указать сайт", callback_data="website"),
            types.InlineKeyboardButton("Указать почту", callback_data="email")
        ]
        markup.add(*buttons)
        bot.send_message(call.message.chat.id, "Выберите, что хотите указать:", reply_markup=markup)

    elif call.data in ["description", "work_type", "cost", "website", "email"]:
        request_data(call)
    elif call.data == "upload_photos":
        bot.send_message(call.message.chat.id, "Пожалуйста, загрузите 3-4 фотографии объектов.")
        bot.register_next_step_handler(call.message, handle_photos)
    elif call.data == "back_to_menu":
        msg_to_profile(call.message.chat.id)
    if deleting_flag:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    user_id = message.json['new_chat_participant']['id']  # TODO REMOVE JOB OF REGISTRATION REMIND BOT 1
    # scheduler.remove_job(f"{user_id}_city_remind")
    if data_base_functions.check_radius_exists(user_id):
        schedule_reminder(user_id, f"{user_id}_register_confirmation_1_remind_second_bot", 2880,
                          text_messages_storage.message_definer(19))
        schedule_reminder(user_id, f"{user_id}_register_confirmation_2_remind_second_bot", 7200,
                          text_messages_storage.message_definer(17))
        schedule_reminder(user_id, f"{user_id}_register_confirmation_3_remind_second_bot", 1080,
                          text_messages_storage.message_definer(18))
        bot.send_message(user_id, text_messages_storage.message_definer(20),
                         reply_markup=config.start_markup())
        typing_action(user_id, 2)
        bot.send_message(user_id, text_messages_storage.message_definer(12))
        typing_action(user_id, 5)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("Как получать заказы на монтаж?", callback_data="wanna_know_more_montage"),
            types.InlineKeyboardButton("Узнать больше о программе лояльности",
                                       callback_data="information_about_referral_program"))  # stupid value name
        bot.send_message(user_id, text_messages_storage.message_definer(13), reply_markup=markup)


def handle_photos(message):
    if message.content_type == 'photo':
        try:
            path_to_images = []
            for media in message.photo:
                file_info = bot.get_file(media.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                photo_path = os.path.join(PHOTO_DIR, f"{message.chat.id}_{file_info.file_unique_id}.jpg")
                path_to_images.append(f"{message.chat.id}_{file_info.file_unique_id}.jpg")
                with open(photo_path, 'wb') as new_file:
                    new_file.write(downloaded_file)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Продолжить заполнение профиля", callback_data="add_additional_information"))
            user = data_base_functions.SQLiteUser(message.chat.id)
            user.change_path_to_images(" ".join(path_to_images))
            bot.send_message(message.chat.id, "Фотографии сохранены.", reply_markup=markup)
        except Exception as er:
            print(er)
            bot.send_message(message.chat.id, "Что-то пошло не так. Попробуйте еще раз или напишите в поддержку.")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, загрузите фотографию.")


def request_data(call):
    messages = {
        "description": "Напишите, какие виды объектов вы берете в работу (гараж, бытовка, ангар, торговые помещения и так далее).",
        "work_type": "Напишите, какие виды работ вы выполняете.",
        "cost": "Укажите среднюю стоимость за м².",
        "website": "Укажите сайт, если есть.",
        "email": "Укажите почту."
    }

    msg = bot.send_message(call.message.chat.id, messages[call.data])
    bot.register_next_step_handler(msg, save_user_data, call.data)


def save_user_data(message, key):
    user_id = message.from_user.id
    user = data_base_functions.SQLiteUser(user_id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Продолжить заполнение профиля", callback_data="add_additional_information"))
    if key == "description":
        user.change_object_description(message.text)
    elif key == "work_type":
        user.change_types_of_completed_works(message.text)
    elif key == "cost":
        user.change_average_price(message.text)
    elif key == "website":
        user.change_path_to_images(message.text)
    elif key == "email":
        user.change_email(message.text)

    bot.send_message(message.chat.id, "<b>Данные сохранены.</b>", reply_markup=markup)


def define_job_markup(user_id, additional_call_data_forward="next_step_registration", flag_is_required=True):
    list_of_jobs = config.define_list_of_jobs(user_id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    if flag_is_required:
        markup.add(types.InlineKeyboardButton("Вернуться назад", callback_data="back_to_start_menu"))
        for job_name in list_of_jobs:
            markup.add(types.InlineKeyboardButton(text=job_name,
                                                  callback_data=f"toggle+/+{config.job_to_variable[job_name]}"))
    else:
        for job_name in list_of_jobs:
            markup.add(types.InlineKeyboardButton(text=job_name,
                                                  callback_data=f"toggle+/+{config.job_to_variable[job_name]}+/+"
                                                                f"{additional_call_data_forward}"))
    markup.add(types.InlineKeyboardButton("Продолжить", callback_data="back_to_menu"))
    return markup


def change_city_name(msg):
    if msg.text == "Назад в меню":
        msg_to_profile(msg.chat.id, True)
    else:
        user = data_base_functions.SQLiteUser(msg.chat.id)
        proposed_city_list = config.find_similar_cities(msg.text)
        if msg.text in proposed_city_list:
            user.change_city(msg.text)
            bot.send_message(msg.chat.id, "Изменения сохранены", reply_markup=config.start_markup())
            msg_to_profile(msg.chat.id)
        elif proposed_city_list:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            for city in proposed_city_list:
                markup.add(types.KeyboardButton(city))
            msg = bot.send_message(msg.chat.id,
                                   f"Такого города нет в списке. Возможно, вы имели в виду:\n"
                                   f"<b><i>{', '.join(proposed_city_list)}</i></b>", reply_markup=markup)
            bot.register_next_step_handler(msg, change_city_name)
        else:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Назад в меню"))
            msg = bot.send_message(msg.chat.id, "Такого города нет в списке, пожалуйста проверьте правильность ввода.",
                                   reply_markup=markup)
            bot.register_next_step_handler(msg, change_city_name)


def change_phone_number(msg):
    if msg.text == "Назад в меню":
        msg_to_profile(msg.chat.id, True)
    else:
        if config.is_valid_phone_number(msg.text):
            user = data_base_functions.SQLiteUser(msg.chat.id)
            user.change_phone_number(msg.text)
            bot.send_message(msg.chat.id, "Изменения сохранены.", reply_markup=config.start_markup())
            msg_to_profile(msg.chat.id)
        else:
            msg = bot.send_message(msg.chat.id, "Номер телефона неправильно указан. Попробуйте еще раз.")
            bot.register_next_step_handler(msg, change_phone_number)


def change_radius(msg):
    if msg.text == "Назад в меню":
        msg_to_profile(msg.chat.id, True)
    else:
        if msg.text.isdigit():
            user = data_base_functions.SQLiteUser(msg.chat.id)
            user.change_radius(int(msg.text))
            bot.send_message(msg.chat.id, "Изменения сохранены.", reply_markup=config.start_markup())
            msg_to_profile(msg.chat.id)
        else:
            msg = bot.send_message(msg.chat.id, "Данные указаны неверно. Введите целое число.")
            bot.register_next_step_handler(msg, change_radius)


def typing_action(user_id: int, seconds: int):
    bot.send_chat_action(user_id, "typing")
    time.sleep(seconds)


def msg_to_profile(user_id: int, back_to_menu_flag=False):
    user = data_base_functions.SQLiteUser(user_id)
    if back_to_menu_flag:
        bot.send_message(user_id, "Возвращено в меню", reply_markup=config.start_markup())
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📋 Изменить виды работ", callback_data="change+/+job_categories"))
    markup.add(types.InlineKeyboardButton("🏙 Изменить город", callback_data="change+/+city_name"))
    markup.add(types.InlineKeyboardButton("📍 Изменить радиус работы", callback_data="change+/+radius"))
    markup.add(types.InlineKeyboardButton("📞 Изменить контактный телефон", callback_data="change+/+phone_number"))
    markup.add(
        types.InlineKeyboardButton("✍️ Дополнительно заполнить профиль", callback_data="add_additional_information"))
    user_data_text = f"""Ваши текущие данные:
            
<b>📋 Виды работ:</b> {", ".join(config.define_list_of_jobs_only_useful(user.user_id))}
🏙 <b>Город:</b> {user.city_name}
📍 <b>Радиус работы:</b> {"Вся Россия" if user.city_name == "Россия" else user.radius}
📞 <b>Контактный телефон:</b> {user.phone_number}
    """
    return bot.send_message(user_id, user_data_text, reply_markup=markup)


def send_reminder(chat_id, text_of_reminder):
    bot.send_message(chat_id, text_of_reminder)


def add_manager(chat_id):
    user = data_base_functions.SQLiteUser(chat_id)
    user.change_manager("Maria")
    text = """Персональный менеджер будет сопровождать вас на всех этапах сделки 📞

<b>Знакомьтесь — Мария
Контактный номер: +7 937 060 24 63</b>

Звоните и пишите, если возникнут сложности!

Объекты реализованные менеджером:
Список объектов

Мария свяжется с вами в ближайшее время с целью знакомства и обсуждения планов."""
    bot.send_message(chat_id, text)


def schedule_reminder(chat_id, message_id, time_to_remind, text_of_reminder):
    run_date = datetime.now() + timedelta(minutes=time_to_remind)
    scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[chat_id, text_of_reminder], id=str(message_id))


def schedule_manager(chat_id):
    run_date = datetime.now() + timedelta(minutes=123)
    scheduler.add_job(add_manager, 'date', run_date=run_date, args=[chat_id], id=f"{chat_id}_manager_search")


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
