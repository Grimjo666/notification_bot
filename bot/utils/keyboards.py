from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# Основные кнопки
button_close = InlineKeyboardButton('❌', callback_data='button_close')
button_main_menu = InlineKeyboardButton('В основное меню', callback_data='button_main_menu')


close_menu = InlineKeyboardMarkup(row_width=1)

close_menu.add(button_main_menu, button_close)


main_menu = InlineKeyboardMarkup(row_width=1)

button_subscribe_menu = InlineKeyboardButton('Подписка', callback_data='button_subscribe_menu')
button_settings_menu = InlineKeyboardButton('Как настроить бота', callback_data='button_settings_menu')
button_account_menu = InlineKeyboardButton('Аккаунт', callback_data='button_account_menu')

main_menu.add(button_subscribe_menu,
              button_settings_menu,
              button_account_menu,
              button_close)


free_subscription_menu = InlineKeyboardMarkup(row_width=1)

button_get_free_subscription = InlineKeyboardButton('Получить пробную подписку', callback_data='button_get_free_subscription')
button_paid_subscription_menu = InlineKeyboardButton('Пропустить', callback_data='button_paid_subscription_menu')

free_subscription_menu.add(button_get_free_subscription,
                           button_paid_subscription_menu,
                           button_main_menu,
                           button_close)


paid_subscription_menu = InlineKeyboardMarkup(row_width=1)

button_base_subscription = InlineKeyboardButton('Базовая подписка', callback_data='button_base_subscription')
button_extended_subscription = InlineKeyboardButton('Расширенная подписка', callback_data='button_extended_subscription')
button_without_limits_subscription = InlineKeyboardButton('Без ограничений', callback_data='button_without_limits_subscription')
button_individual_subscription = InlineKeyboardButton('1 Fansly аккаунт', callback_data='button_individual_subscription')

paid_subscription_menu.add(button_base_subscription,
                           button_extended_subscription,
                           button_without_limits_subscription,
                           button_individual_subscription,
                           button_main_menu,
                           button_close)


account_menu = InlineKeyboardMarkup(row_width=1)

button_edit_notification_name = InlineKeyboardButton('Изменить имя уведомления', callback_data='button_edit_notification_name')
button_add_user_to_account = InlineKeyboardButton('Добавить пользователя в аккаунт', callback_data='button_add_user_to_account')
button_del_user_from_account = InlineKeyboardButton('Удалить пользователя из аккаунта', callback_data='button_del_user_from_account')


account_menu.add(button_edit_notification_name,
                 button_add_user_to_account,
                 button_del_user_from_account,
                 button_main_menu,
                 button_close)


notification_menu = InlineKeyboardMarkup(row_width=1)

button_switch_notifications = InlineKeyboardButton('Включить/выключить уведомления', callback_data='button_switch_notifications')
button_add_filters = InlineKeyboardButton('Добавить фильтры на уведомления', callback_data='button_add_filters')

notification_menu.add(button_switch_notifications, button_add_filters, button_main_menu, button_close)


transition_account_menu = InlineKeyboardMarkup(row_width=1)

button_notification_menu = InlineKeyboardButton('Управление личными уведомлениями', callback_data='button_notification_menu')
button_account_menu_control = InlineKeyboardButton('Управление аккаунтом', callback_data='button_account_menu_control')

transition_account_menu.add(button_notification_menu, button_account_menu_control, button_main_menu, button_close)

# def create_models_keyboard():
#     models = get_all_emails()
#     keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
#     if models is not None:
#         for model in models:
#             keyboard.add(KeyboardButton(f'{model[0]} / {model[1]}'))
#     return keyboard


# def create_users_keyboard():
#     users = get_all_users()
#     if len(users) > 0:
#         keyboard = ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=False)
#         for user in users:
#             keyboard.add(KeyboardButton(f'{user[0]} / {user[1]}'))
#         return keyboard
#     return False
#
#
# def create_notification_keyboard(user_id):
#     notifications = db_control.get_all_user_email_notification(user_id)
#     if len(notifications) > 0:
#         keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
#         for ntf in notifications:
#             name = db_control.get_email_name(ntf[0])[0]
#             button = KeyboardButton(f'{ntf[0]} / {name}')
#             keyboard.add(button)
#         return keyboard
#     return False

