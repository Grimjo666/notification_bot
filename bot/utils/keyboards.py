from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from bot.services.db_control import get_all_emails, get_all_users
from bot.services import db_control

# Основные кнопки
button_close = InlineKeyboardButton('❌', callback_data='button_close')
button_main_menu = InlineKeyboardButton('В основное меню', callback_data='button_main_menu')


close_menu = InlineKeyboardMarkup(row_width=1)

close_menu.add(button_main_menu, button_close)


main_admin_menu = InlineKeyboardMarkup(row_width=1)

button_edit_model_name = InlineKeyboardButton('Редактировать список уведомлений', callback_data='button_edit_model_name_menu')
button_add_notification = InlineKeyboardButton('Добавить уведомление', callback_data='button_add_notification_menu')
button_del_notification = InlineKeyboardButton('Убрать уведомление', callback_data='button_del_notification_menu')
button_add_user_to_bot = InlineKeyboardButton('Дать доступ к боту', callback_data='button_add_user_menu')
button_del_access_from_bot = InlineKeyboardButton('Убрать доступ', callback_data='button_del_user_menu')

main_admin_menu.add(button_edit_model_name,
                    button_add_notification,
                    button_del_notification,
                    button_add_user_to_bot,
                    button_del_access_from_bot,
                    button_close)


admin_menu = InlineKeyboardMarkup(row_width=1)

admin_menu.add(button_add_notification, button_del_notification, button_close)


del_model_name_menu = InlineKeyboardMarkup(row_width=1)

button_del_model_name_keyboard = InlineKeyboardButton('Удалить уведомление', callback_data='button_del_model_name_keyboard')

del_model_name_menu.add(button_del_model_name_keyboard, button_main_menu, button_close)


def create_models_keyboard():
    models = get_all_emails()
    keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
    if models is not None:
        for model in models:
            keyboard.add(KeyboardButton(f'{model[0]} / {model[1]}'))
    return keyboard


def create_users_keyboard():
    users = get_all_users()
    if len(users) > 0:
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=False)
        for user in users:
            keyboard.add(KeyboardButton(f'{user[0]} / {user[1]}'))
        return keyboard
    return False


def create_notification_keyboard(user_id):
    notifications = db_control.get_all_user_email_notification(user_id)
    if len(notifications) > 0:
        keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
        for ntf in notifications:
            name = db_control.get_email_name(ntf[0])[0]
            button = KeyboardButton(f'{ntf[0]} / {name}')
            keyboard.add(button)
        return keyboard
    return False


notification_menu = InlineKeyboardMarkup(row_width=1)

button_show_models = InlineKeyboardButton('Показать доступные уведомления', callback_data='button_show_models')
button_add_all = InlineKeyboardButton('Добавить все уведомления', callback_data='button_add_all_notification')

notification_menu.add(button_show_models, button_add_all, button_main_menu, button_close)


del_notification_menu = InlineKeyboardMarkup(row_width=1)

button_your_notification = InlineKeyboardButton('Активные уведомления', callback_data='button_your_notification')
button_del_all_notification = InlineKeyboardButton('Убрать все уведомления', callback_data='button_del_all_notification')

del_notification_menu.add(button_your_notification, button_del_all_notification, button_main_menu, button_close)


del_user_menu = InlineKeyboardMarkup(row_width=1)

button_show_users = InlineKeyboardButton('Показать пользователей с доступом', callback_data='button_show_users')

del_user_menu.add(button_show_users, button_main_menu, button_close)

