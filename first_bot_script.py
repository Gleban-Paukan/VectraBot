import time
import sys
import telebot
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from datetime import datetime, timedelta
from telebot import types
from requests import ReadTimeout
import os
import data_base_functions
import config
import text_messages_storage

bot = telebot.TeleBot(config.first_bot_token())
bot.parse_mode = 'html'

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton(text="Пройти регистрацию", callback_data="start_of_registration"))
    markup.add(
        types.InlineKeyboardButton(text="Узнать больше о клубе", callback_data="additional_club_information"),
        types.InlineKeyboardButton(text="Правила клуба", callback_data="club_rules"),
        types.InlineKeyboardButton(text="Получить консультацию по телефону", callback_data="ZAGLUSHKA"),  # TODO
        types.InlineKeyboardButton(text="Корпоративный сайт", url="https://vektragroup.ru/")
    )

    bot.send_message(message.chat.id, text_messages_storage.message_definer(1), reply_markup=markup)
    data_base_functions.SQLiteUser(message.chat.id, message.from_user.username)


@bot.message_handler(content_types=['location'])
def handle_location(message):
    scheduler.remove_job(f"{message.chat.id}_location_remind")
    location = message.location
    lat, long = location.latitude, location.longitude
    user = data_base_functions.SQLiteUser(message.chat.id)
    user.change_position(lat, long)

    remove_markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(message.chat.id,
                           "Теперь введите максимальную дальность (в километрах). Её можно будет изменить.",
                           reply_markup=remove_markup)
    bot.register_next_step_handler(msg, set_radius_registration)


@bot.message_handler(content_types=['text'])
def text_message_handler(message):
    if message.text == "Получить баллы":  # full cringe is coming (sorry, just too lazy)
        try:
            text_to_remind = ("Вы уверены, что не хотите вступить в закрытый чат монтажников?\n"
                              "Напоминаем что там есть возможность задавать вопросы, обмен опытом, "
                              "участие в обсуждениях, развитие навыков и конечно же получение заказов!)\n\n"
                              "Применяйте опыт нескольких сотен профессионалов, для увеличения Вашего дохода от "
                              "монтажа и повышения лояльности заказчика!")
            schedule_reminder(message.chat.id, f"{message.chat.id}_register_confirmation_1_remind", 30, text_to_remind)
            text_to_remind = "Вы не можете завершить регистрацию без вступления в закрытый чат"
            schedule_reminder(message.chat.id, f"{message.chat.id}_register_confirmation_2_remind", 120, text_to_remind)
        except Exception as eerr:
            print(eerr)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Подписаться", url="https://t.me/+wxQ8vd1p-GxhYjFl"))
        markup.add(types.InlineKeyboardButton("Я подписался", callback_data="check_subscription_stage"))
        bot.send_message(
            message.chat.id, "Подпишитесь на закрытый Telegram-чат клуба, чтобы быть в курсе всех новостей: "
                             "закрытая информация по ценам и квотам с производственных площадок, данные о "
                             "наличии продукции и многое другое.", reply_markup=markup)
    elif message.text == "Подробнее про программу лояльности":
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Получить баллы"),
                   types.KeyboardButton("Подробнее про программу лояльности"))
        markup.add(types.KeyboardButton("Личный кабинет"))
        bot.send_message(message.chat.id, "<b>Знакомим вас подробнее с системой программы лояльности</b>")
        typing_action(message.chat.id, 1)
        bot.send_message(message.chat.id, text_messages_storage.message_definer(9))
        typing_action(message.chat.id, 4)
        bot.send_message(message.chat.id, "<b>Но это еще не все! Сейчас расскажем, какие дополнительные преимущества "
                                          "вы получите, воспользовавшись нашей программой лояльности. </b>")
        typing_action(message.chat.id, 5)
        bot.send_message(message.chat.id, text_messages_storage.message_definer(10))
        typing_action(message.chat.id, 1)
        bot.send_message(message.chat.id, "<b>Уже захотелось стать участником программы лояльности? "
                                          "А чтобы окончательно отбросить все ваши сомнения рассказываем об акциях и"
                                          " бонусах в рамках программы: </b>")
        typing_action(message.chat.id, 6)
        bot.send_message(message.chat.id, text_messages_storage.message_definer(11), reply_markup=markup)
    elif message.text == "Далее":
        scheduler.remove_job(f"{message.chat.id}_location_remind")
        user = data_base_functions.SQLiteUser(message.chat.id)
        user.change_radius(9999)
        typing_action(message.chat.id, 2)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Поделиться контактом", request_contact=True))
        bot.send_message(message.chat.id, text_messages_storage.message_definer(6), reply_markup=markup)
    elif message.text == "Личный кабинет":
        msg_to_profile(message.chat.id)


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    user = data_base_functions.SQLiteUser(message.chat.id)
    user.change_phone_number(message.contact.phone_number)
    user_data_text = f"""
<b>📋 Виды работ:</b> {", ".join(config.define_list_of_jobs_only_useful(user.user_id))}
<b>🏙 Город:</b> {user.city_name}
<b>📍 Радиус работы:</b> {"Вся Россия" if user.city_name == "Россия" else user.radius}
📞 <b>Контактный телефон:</b> {user.phone_number}
""" + text_messages_storage.message_definer(7)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Завершить регистрацию", callback_data="finish_registration"))
    bot.send_message(message.chat.id, user_data_text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def inline_handler(call):
    deleting_flag = True
    if call.message:
        if call.data == "additional_club_information":
            bot.send_message(call.message.chat.id, "<b>Мы рады, что вы хотите узнать больше о клубе монтажников!</b>")
            typing_action(call.message.chat.id, 1)
            bot.send_message(call.message.chat.id, text_messages_storage.message_definer(2))
            typing_action(call.message.chat.id, 5)
            bot.send_message(call.message.chat.id,
                             "<b>А теперь давайте рассмотрим,"
                             " какие привилегии предоставляет закрытый клуб монтажников</b>")
            typing_action(call.message.chat.id, 3)
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text="Пройти регистрацию", callback_data="start_of_registration"))
            markup.add(types.InlineKeyboardButton(text="Вернуться назад", callback_data="back_to_start_menu"))
            markup.add(
                types.InlineKeyboardButton(text="Получить консультацию по телефону", callback_data="ZAGLUSHKA"))  # TODO

            bot.send_message(call.message.chat.id, text_messages_storage.message_definer(3), reply_markup=markup)
        elif call.data == "start_of_registration":
            bot.send_message(call.message.chat.id, "Ежемесячно мы получаем около 👉 5 000 заявок на поставку и монтаж "
                                                   "зданий из сэндвич-панелей площадью от 800 м2.")
            typing_action(call.message.chat.id, 1)
            markup = define_job_markup(call.message.chat.id)
            with open("woman_offer.jpeg", 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo=photo,
                               caption="Хотите получить доступ к этим заказам? <b>Укажите "
                                       "виды работ, которые вы выполняете:</b>", reply_markup=markup)
        elif call.data == "next_step_registration":
            msg = bot.send_message(call.message.chat.id, text_messages_storage.message_definer(4))
            text_to_remind = """Кажется, Вы забыли указать свой город. Давайте попробуем снова: из какого вы города?
Нам необходима эта информация, чтобы сузить географию работ, когда мы будем искать для вас подходящий заказ"""
            schedule_reminder(msg.chat.id, f"{msg.chat.id}_city_remind", 30, text_to_remind)
            bot.register_next_step_handler(msg, registration_city_defining)
        elif call.data == "back_to_start_menu":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton(text="Пройти регистрацию", callback_data="start_of_registration"))
            markup.add(
                types.InlineKeyboardButton(text="Правила клуба", callback_data="club_rules"),
                types.InlineKeyboardButton(text="Получить консультацию по телефону", callback_data="ZAGLUSHKA"),  # TODO
                types.InlineKeyboardButton(text="Корпоративный сайт", url="https://vektragroup.ru/")
            )
            bot.send_message(call.message.chat.id, "Возвращено в стартовое меню", reply_markup=markup)
        elif call.data == "finish_registration":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Получить баллы"),
                       types.KeyboardButton("Подробнее про программу лояльности"))
            markup.add(types.KeyboardButton("Личный кабинет"))
            with open("referral_instructions.png", 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo,
                               caption=text_messages_storage.message_definer(8), reply_markup=markup)
            user = data_base_functions.SQLiteUser(call.message.chat.id)
            bot.send_message(call.message.chat.id, text=text_messages_storage.message_definer(16))
        elif call.data == "back_to_profile":
            msg_to_profile(call.message.chat.id)
        elif call.data == "check_subscription_stage":
            if is_user_in_channel(call.message.chat.id, config.id_of_chat_vectra_montajniki()):
                bot.send_message(call.message.chat.id, "Регистрация завершена.")
                try:  # TODO SORRY FOR POOR CODE
                    scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_2_remind")
                    scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_1_remind")
                except Exception as er:
                    print("Small job conflict, it OK :)", er)
            else:
                bot.answer_callback_query(call.id, "Для завершения регистрации необходимо вступить в чат.",
                                          show_alert=True)
                deleting_flag = False
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

        if deleting_flag:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


# def change_job_category(msg):
#     markup = define_job_markup(msg.chat.id)
#     markup.add(types.InlineKeyboardButton("Вернуться назад", callback_data="back_to_profile"))
#     bot.send_message(msg.chat.id, "Укажите, какие категории хотите добавить или убрать.", reply_markup=markup)


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
    markup.add(types.InlineKeyboardButton("Продолжить", callback_data=additional_call_data_forward))
    return markup


def change_city_name(msg):
    if msg.text == "Назад в меню":
        msg_to_profile(msg.chat.id)
    else:
        user = data_base_functions.SQLiteUser(msg.chat.id)
        proposed_city_list = config.find_similar_cities(msg.text)
        if msg.text in proposed_city_list:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Получить баллы"),
                       types.KeyboardButton("Подробнее про программу лояльности"))
            markup.add(types.KeyboardButton("Личный кабинет"))
            user.change_city(msg.text)
            bot.send_message(msg.chat.id, "Изменения сохранены", reply_markup=markup)
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
        msg_to_profile(msg.chat.id)
    else:
        if config.is_valid_phone_number(msg.text):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Получить баллы"),
                       types.KeyboardButton("Подробнее про программу лояльности"))
            markup.add(types.KeyboardButton("Личный кабинет"))
            user = data_base_functions.SQLiteUser(msg.chat.id)
            user.change_phone_number(msg.text)
            bot.send_message(msg.chat.id, "Изменения сохранены.", reply_markup=markup)
            msg_to_profile(msg.chat.id)
        else:
            msg = bot.send_message(msg.chat.id, "Номер телефона неправильно указан. Попробуйте еще раз.")
            bot.register_next_step_handler(msg, change_phone_number)


def change_radius(msg):
    if msg.text == "Назад в меню":
        msg_to_profile(msg.chat.id)
    else:
        if msg.text.isdigit():
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(types.KeyboardButton("Получить баллы"),
                       types.KeyboardButton("Подробнее про программу лояльности"))
            markup.add(types.KeyboardButton("Личный кабинет"))
            user = data_base_functions.SQLiteUser(msg.chat.id)
            user.change_radius(int(msg.text))
            bot.send_message(msg.chat.id, "Изменения сохранены.", reply_markup=markup)
            msg_to_profile(msg.chat.id)
        else:
            msg = bot.send_message(msg.chat.id, "Данные указаны неверно. Введите целое число.")
            bot.register_next_step_handler(msg, change_radius)


def msg_to_profile(user_id: int):
    user = data_base_functions.SQLiteUser(user_id)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("📋 Изменить виды работ", callback_data="change+/+job_categories"))
    markup.add(types.InlineKeyboardButton("🏙 Изменить город", callback_data="change+/+city_name"))
    markup.add(types.InlineKeyboardButton("📍 Изменить радиус работы", callback_data="change+/+radius"))
    markup.add(types.InlineKeyboardButton("📞 Изменить контактный телефон", callback_data="change+/+phone_number"))
    user_data_text = f"""Ваши текущие данные:
            
<b>📋 Виды работ:</b> {", ".join(config.define_list_of_jobs_only_useful(user.user_id))}
🏙 <b>Город:</b> {user.city_name}
📍 <b>Радиус работы:</b> {"Вся Россия" if user.city_name == "Россия" else user.radius}
📞 <b>Контактный телефон:</b> {user.phone_number}
    """
    return bot.send_message(user_id, user_data_text, reply_markup=markup)


def typing_action(user_id: int, seconds: int):
    bot.send_chat_action(user_id, "typing")
    time.sleep(seconds)


def set_radius_registration(msg):
    if msg.text.isdigit():
        if int(msg.text) <= 0 or int(msg.text) >= 40192:
            bot.send_message(msg.chat.id, "Пожалуйста, введите радиус. Число, больше нуля и меньше 40192.")
            bot.register_next_step_handler(msg, set_radius_registration)
            return
        user = data_base_functions.SQLiteUser(msg.chat.id)
        user.change_radius(int(msg.text))
        typing_action(msg.chat.id, 2)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Поделиться контактом", request_contact=True))
        bot.send_message(msg.chat.id, text_messages_storage.message_definer(6), reply_markup=markup)
    else:
        bot.send_message(msg.chat.id, "Пожалуйста, введите радиус (только число).")
        bot.register_next_step_handler(msg, set_radius_registration)


def is_user_in_channel(user_id, channel_id):
    try:
        member = bot.get_chat_member(channel_id, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except telebot.apihelper.ApiTelegramException as e:
        print(f"Error: {e}")
        return False


def registration_city_defining(msg):
    user = data_base_functions.SQLiteUser(msg.chat.id)
    proposed_city_list = config.find_similar_cities(msg.text)
    if msg.text in proposed_city_list:
        scheduler.remove_job(f"{msg.chat.id}_city_remind")
        text_to_remind = ("Указание радиуса работ необходимо для того, чтобы координатор клуба имел представление "
                          "о географии вашей деятельности. Это позволит ему лучше понимать, на какие заказы вы можете "
                          "претендовать и насколько быстро сможете добраться до места работы.\n\n"
                          "Вы не указали радиус, давайте сделаем ещё одну попытку.")
        schedule_reminder(msg.chat.id, f"{msg.chat.id}_location_remind", 30, text_to_remind)
        user.change_city(msg.text)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("Поделиться геолокацией", request_location=True))
        markup.add(types.KeyboardButton("Далее"))
        with open("geo_of_radius.png", 'rb') as photo:
            bot.send_photo(msg.chat.id, photo, caption=text_messages_storage.message_definer(5),
                           reply_markup=markup)
    elif proposed_city_list:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for city in proposed_city_list:
            markup.add(types.KeyboardButton(city))
        msg = bot.send_message(msg.chat.id,
                               f"Такого города нет в списке. Возможно, вы имели в виду:\n"
                               f"<b><i>{', '.join(proposed_city_list)}</i></b>", reply_markup=markup)
        bot.register_next_step_handler(msg, registration_city_defining)
    else:
        msg = bot.send_message(msg.chat.id, "Такого города нет в списке, пожалуйста проверьте правильность ввода.")
        bot.register_next_step_handler(msg, registration_city_defining)


def send_reminder(chat_id, text_of_reminder):
    bot.send_message(chat_id, text_of_reminder)


def schedule_reminder(chat_id, message_id, time_to_remind, text_of_reminder):
    run_date = datetime.now() + timedelta(minutes=time_to_remind)
    scheduler.add_job(send_reminder, 'date', run_date=run_date, args=[chat_id, text_of_reminder], id=str(message_id))


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
