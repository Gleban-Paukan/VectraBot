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
designer_bot = telebot.TeleBot(config.designer_bot_token())
admin_bot = telebot.TeleBot(config.third_bot_token())
admin_bot.parse_mode = "html"
designer_bot.parse_mode = "html"
bot.parse_mode = 'html'

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
}
scheduler = BackgroundScheduler(jobstores=jobstores)
scheduler.start()
photos_dict = {}
user_states = {}
designers = [1493818085, 1125076741]  # 1223719258


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


@bot.message_handler(
    func=lambda message: message.chat.id in user_states and user_states[message.chat.id]['expected_photos'] == 0,
    content_types=['text'])
def set_expected_photos(message):
    """Устанавливает ожидаемое количество фотографий в альбоме от пользователя."""
    try:
        if message.text == "/cancel":
            bot.send_message(message.chat.id, "Ввод фотографий отменен.")
            del user_states[message.chat.id]
            return
        num_photos = int(message.text)
        if num_photos <= 0:
            raise ValueError("Количество фотографий должно быть больше 0.")
        if num_photos == 1:
            bot.send_message(message.chat.id,
                             "Необходимо загрузить более одной фотографии. Попробуйте еще раз.\n"
                             "Нажмите <b>/cancel</b>, чтобы отменить ввод")
            return
        elif num_photos >= 10:
            bot.send_message(message.chat.id,
                             "Слишком много фотографий. Попробуйте еще раз.\n"
                             "Нажмите <b>/cancel</b>, чтобы отменить ввод")
            return
        user_states[message.chat.id]['expected_photos'] = num_photos
        bot.send_message(message.chat.id, f"Отправьте {num_photos} фотографий.")
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите правильное количество фотографий.")


@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    """Обрабатывает фотографии, добавляя их в список для текущего пользователя, и сохраняет их по достижении нужного количества."""
    chat_id = message.chat.id

    # Проверяем, ожидает ли пользователь загрузку фотографий
    if chat_id in user_states:
        user_states[chat_id]

        # Проверяем, установлено ли ожидаемое количество фотографий и не превышено ли оно
        if user_states[chat_id]['expected_photos'] > 0 and user_states[chat_id]['received_photos'] < \
                user_states[chat_id]['expected_photos']:
            # Получаем информацию о фото в самом высоком разрешении и сохраняем его
            file_info = bot.get_file(message.photo[-1].file_id)  # Используем самое большое разрешение фото
            downloaded_file = bot.download_file(file_info.file_path)
            photo_path = os.path.join(PHOTO_DIR, f"{chat_id}_{file_info.file_unique_id}.jpg")

            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Добавляем путь к сохраненной фотографии
            user_states[chat_id]['photos'].append(photo_path)
            user_states[chat_id]['received_photos'] += 1
            # Если все фотографии получены, сохраняем их в базу данных и отправляем сообщение
            if user_states[chat_id]['received_photos'] == user_states[chat_id]['expected_photos']:
                save_album_to_db(chat_id, user_states[chat_id]['photos'])
                # Очищаем состояние пользователя
                del user_states[chat_id]


def save_album_to_db(chat_id, photo_paths):
    """Сохраняет все фото из альбома в базу данных и отправляет сообщение об успешном сохранении."""
    path_to_images = " ".join(photo_paths)
    user = data_base_functions.SQLiteUser(chat_id)
    user.change_path_to_images(path_to_images)

    # Отправляем сообщение пользователю
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Продолжить заполнение профиля", callback_data="add_additional_information"))
    bot.send_message(chat_id, "Все фотографии сохранены успешно.", reply_markup=markup)


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
        bot.send_message(message.chat.id, text_messages_storage.message_definer(24))
    elif message.text == "🏚 Мои заказы":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("История заказов", callback_data="order_list"),
                   types.InlineKeyboardButton("Отправить заявку на просчет",
                                              callback_data="application_for_miscalculation"))
        bot.send_message(message.chat.id, "Выберите опцию", reply_markup=markup)
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
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(23),
                         reply_markup=config.start_markup())
    elif call.data == "order_list":
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        if user.orders_id is None:
            bot.send_message(call.message.chat.id, text_messages_storage.message_definer(22))
        else:
            if len(user.orders_id.split()) > 1:
                bot.send_message(call.message.chat.id, "Список ваших заказов:")
            for order_id in user.orders_id.split():
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
                bot.send_message(call.message.chat.id, text)
                deleting_flag = False
    elif call.data == "application_for_miscalculation":
        bot.send_message(call.message.chat.id, text_messages_storage.message_definer(24))
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
    elif "order+/+" in call.data:
        order_id = call.data.split("+/+")[1]
        order_data = data_base_functions.get_order_data(order_id)[0]
        square = order_data[1]
        city = order_data[2]
        jobs = order_data[3].split(",")
        address = order_data[4]
        status = order_id[5]
        if status != "WAITING":
            bot.send_message(call.message.chat.id, "К сожалению, этот заказ уже выполняет другой исполнитель")
            return
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        user.add_order(order_id)
        bot.send_message(call.message.chat.id,
                         "Отлично! Скоро с Вами свяжется ваш персональный менеджер и уточнит детали заказа.")
        text = f"""
На заявку <code>{order_id}</code> откликнулись!

Информация по заявке:

Виды работ:
<b>
{'\n'.join(jobs)}
</b>
Объект по адресу: {city}, {address}
Объем: {square} м²

Информация по заказчику:


Telegram ID: <code>{user.user_id}</code>
AMOCRM ID: <code>{user.lead_id}</code>
Номер телефона: <b>{user.phone_number}</b>
"""
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("Подтвердить заказ", callback_data=f"confirm_order+/+{call.message.chat.id}+/+{order_id}"))
        for admin_id in data_base_functions.get_admins_list()[0]:
            admin_bot.send_message(admin_id, text, reply_markup=markup)
    elif call.data == "add_additional_information":
        markup = types.InlineKeyboardMarkup(row_width=2)
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        buttons = [
            types.InlineKeyboardButton(f"{user.define_check_mark('object_description')} Описание объекта",
                                       callback_data="description"),
            types.InlineKeyboardButton(f"{user.define_check_mark('types_of_completed_works')} Вид выполненных работ",
                                       callback_data="work_type"),
            types.InlineKeyboardButton(f"{user.define_check_mark('average_price')} Средняя стоимость за м²",
                                       callback_data="cost"),
            types.InlineKeyboardButton(f"{user.define_check_mark('path_to_images')} Загрузить фотографии",
                                       callback_data="upload_photos"),
            types.InlineKeyboardButton(f"{user.define_check_mark('email')} Указать сайт", callback_data="website"),
            types.InlineKeyboardButton(f"{user.define_check_mark('site')} Указать почту", callback_data="email"),
            types.InlineKeyboardButton(
                f"{user.define_check_mark('path_to_portfolio')} Отправить заявку на создание портфолио",
                callback_data="request_portfolio")
        ]
        markup.add(*buttons)
        bot.send_message(call.message.chat.id, "Выберите, что хотите указать:", reply_markup=markup)

    elif call.data in ["description", "work_type", "cost", "website", "email"]:
        request_data(call)
    elif call.data == "upload_photos":
        bot.send_message(call.message.chat.id, "Введите количество фотографий, которые хотите загрузить (3-4 фото).")
        user_states[call.message.chat.id] = {'expected_photos': 0, 'received_photos': 0, 'photos': []}
        # bot.register_next_step_handler(call.message, handle_photos)
    elif call.data == "request_portfolio":
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        user_data = [user.__getattribute__(i) for i in ["object_description", "types_of_completed_works",
                                                        "average_price", "path_to_images", "email"]]
        if any(i is None for i in user_data):
            bot.answer_callback_query(call.id, "Чтобы отправить заявку дизайнеру, необходимо заполнить все данные.")
            return

        text = f"""
Проверьте, пожалуйста, данные:

🏢 Описание объекта: <b>{user.object_description}</b>
🛠 Вид выполненных работ: <b>{user.types_of_completed_works}</b>
💰 Средняя стоимость за м²: <b>{user.average_price}</b>
📧 Электронная почта: <b>{user.email}</b>
🌐 Сайт{" не указан" if user.site is None else f': <b>{user.site}</b>'}
"""
        media = []
        for path in user.path_to_images.split():
            media.append(types.InputMediaPhoto(types.InputFile(path)))
        bot.send_media_group(call.message.chat.id, media=media)
        markup = types.InlineKeyboardMarkup(row_width=1)
        buttons = [types.InlineKeyboardButton("Нет, изменить данные.", callback_data="add_additional_information"),
                   types.InlineKeyboardButton("Отправить заявку дизайнеру", callback_data="send_to_designer")]
        markup.add(*buttons)
        deleting_flag = False
        bot.send_message(call.message.chat.id, text, reply_markup=markup)

    elif call.data == "send_to_designer":
        user = data_base_functions.SQLiteUser(call.message.chat.id)
        text = f"""
Поступила новая заявка на портфолио:
ID: <code>{user.user_id}</code>

🏢 Описание объекта: <b>{user.object_description}</b>
🛠 Вид выполненных работ: <b>{user.types_of_completed_works}</b>
💰 Средняя стоимость за м²: <b>{user.average_price}</b>
📧 Электронная почта: <b>{user.email}</b>
🌐 Сайт{" не указан" if user.site is None else f': <b>{user.site}</b>'}
"""
        media = []
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(types.InlineKeyboardButton("Отправить портфолио", callback_data=f"request_pdf_{user.user_id}"))
        for path in user.path_to_images.split():
            media.append(types.InputMediaPhoto(types.InputFile(path)))
        for designer in designers:
            designer_bot.send_media_group(designer, media=media)
            designer_bot.send_message(designer, text, reply_markup=markup)
        bot.send_message(call.message.chat.id,
                         "Заявка отправлена. Обычно наш дизайнер обрабатывает заявки в течение одного рабочего дня.")
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


# @bot.message_handler(content_types=['photo'])
# def handle_photos(message):
#     # Если сообщение принадлежит альбому (группе медиафайлов)
#     if message.media_group_id:
#         # Проверяем, есть ли уже записи для текущего media_group_id
#         if message.media_group_id not in photos_dict:
#             photos_dict[message.media_group_id] = []
#
#         # Получаем информацию о фото в самом высоком разрешении и сохраняем его
#         file_info = bot.get_file(message.photo[-1].file_id)  # Используем самое большое разрешение фото
#         downloaded_file = bot.download_file(file_info.file_path)
#         photo_path = os.path.join(PHOTO_DIR, f"{message.chat.id}_{file_info.file_unique_id}.jpg")
#
#         with open(photo_path, 'wb') as new_file:
#             new_file.write(downloaded_file)
#
#         # Добавляем путь к сохраненной фотографии
#         photos_dict[message.media_group_id].append(photo_path)
#
#     # Если фото не принадлежит альбому, просто обрабатываем его отдельно
#     if not message.media_group_id:
#         handle_single_photo(message)
#
#     # Если мы получили все фотографии из альбома, отправляем их пользователю
#     # Обычно Telegram отправляет альбом в пределах нескольких секунд, поэтому проверяем длину списка
#     if len(photos_dict[
#                message.media_group_id]) >= 2:  # Устанавливаем порог на основе ожидаемого количества фотографий в альбоме
#         save_album_to_db(message.chat.id, message.media_group_id)


# def save_album_to_db(chat_id, media_group_id):
#     """Сохраняет все фото из альбома в базу данных."""
#     path_to_images = " ".join(photos_dict[media_group_id])
#     user = data_base_functions.SQLiteUser(chat_id)
#     user.change_path_to_images(path_to_images)
#
#     # Очистка временного хранилища после обработки
#     print(photos_dict)
#     # del photos_dict[media_group_id]
#
#     # Отправляем сообщение пользователю
#     markup = types.InlineKeyboardMarkup(row_width=1)
#     markup.add(types.InlineKeyboardButton("Продолжить заполнение профиля", callback_data="add_additional_information"))
#     bot.send_message(chat_id, "Фотографии сохранены.", reply_markup=markup)
#
#
# def handle_single_photo(message):
#     """Обработка и сохранение одиночного фото."""
#     file_info = bot.get_file(message.photo[-1].file_id)  # Используем самое большое разрешение фото
#     downloaded_file = bot.download_file(file_info.file_path)
#     photo_path = os.path.join(PHOTO_DIR, f"{message.chat.id}_{file_info.file_unique_id}.jpg")
#
#     with open(photo_path, 'wb') as new_file:
#         new_file.write(downloaded_file)
#
#     # Сохраняем путь в базу данных
#     user = data_base_functions.SQLiteUser(message.chat.id)
#     user.change_path_to_images(photo_path)
#
#     # Отправляем сообщение пользователю
#     bot.send_message(message.chat.id, "Фотография сохранена.")

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
        user.change_site(message.text)
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
    run_date = datetime.now() + timedelta(minutes=72)
    scheduler.add_job(add_manager, 'date', run_date=run_date, args=[chat_id], id=f"{chat_id}_manager_search")


if __name__ == '__main__':
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (ConnectionError, ReadTimeout) as e:
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
