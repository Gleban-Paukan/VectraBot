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

bot = telebot.TeleBot(config.second_bot_token())
bot.parse_mode = 'html'

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()


@bot.message_handler(commands=['start'])
def start_message_handler(message):
    pass


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
        bot.send_message(message.chat.id, "TODO")



@bot.callback_query_handler(func=lambda call: True)
def inline_handler(call):
    deleting_flag = True
    if call.data == "wanna_know_more":
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_1_remind")
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_2_remind")
        scheduler.remove_job(f"{call.message.chat.id}_register_confirmation_3_remind")
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Да", callback_data="example_message"),
                   types.InlineKeyboardButton("Нет", callback_data="dont_need_example_message"))
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(14), reply_markup=markup)
    elif call.data == "example_message":
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(types.InlineKeyboardButton("Мне интересно", callback_data="ZAGLUSHKA"))
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(15))
    elif call.data == "information_about_referral_program":
        bot.send_message(call.message.chat.id, "<b>Знакомим вас подробнее с системой программы лояльности</b>")
        typing_action(call.message.chat.id, 1)
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(9))
        typing_action(call.message.chat.id, 4)
        bot.send_message(call.message.chat.id,
                         "<b>Но это еще не все! Сейчас расскажем, какие дополнительные преимущества "
                         "вы получите, воспользовавшись нашей программой лояльности. </b>")
        typing_action(call.message.chat.id, 5)
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(10))
        typing_action(call.message.chat.id, 1)
        bot.send_message(call.message.chat.id, "<b>Уже захотелось стать участником программы лояльности? "
                                               "А чтобы окончательно отбросить все ваши сомнения рассказываем об акциях"
                                               " и бонусах в рамках программы: </b>")
        typing_action(call.message.chat.id, 6)
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(11),
                         reply_markup=config.start_markup())

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
    elif call.data == "back_to_menu":
        msg_to_profile(call.message.chat.id)
    if deleting_flag:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(content_types=['new_chat_members'])
def new_member_handler(message):
    user_id = message.json['new_chat_participant']['id']
    if data_base_functions.check_radius_exists(user_id):
        schedule_reminder(user_id, f"{user_id}_register_confirmation_1_remind", 2880, "text_to_remind1")
        schedule_reminder(user_id, f"{user_id}_register_confirmation_2_remind", 7200, "text_to_remind2")
        schedule_reminder(user_id, f"{user_id}_register_confirmation_3_remind", 1080, "text_to_remind3")
        bot.send_message(user_id, "Привет! На связи виртуальный ассистент клуба @name (Надо придумать)",
                         reply_markup=config.start_markup())
        typing_action(user_id, 2)
        bot.send_message(user_id, text_messages_storage.message_definer(12))
        typing_action(user_id, 5)
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("Хотите узнать больше?", callback_data="wanna_know_more"))  # stupid value name
        bot.send_message(user_id, text_messages_storage.message_definer(13), reply_markup=markup)


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
    user_data_text = f"""Ваши текущие данные:
            
<b>📋 Виды работ:</b> {", ".join(config.define_list_of_jobs_only_useful(user.user_id))}
🏙 <b>Город:</b> {user.city_name}
📍 <b>Радиус работы:</b> {"Вся Россия" if user.city_name == "Россия" else user.radius}
📞 <b>Контактный телефон:</b> {user.phone_number}
    """
    return bot.send_message(user_id, user_data_text, reply_markup=markup)


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
