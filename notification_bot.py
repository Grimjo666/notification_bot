import logging
import asyncio
import os

import sys
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
import aiogram.utils.exceptions as aiogram_exceptions


from bot.create_bot import dp, bot
from bot.handlers import main_menu_handlers, subscription_handlers,\
    account_menu_handlers, notification_menu_handlers, admin_menu_handlers
from data.create_db import create_database

from bot.services import background_tasks

# Настройка логирования
logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.ERROR,
#                     filename='bot_errors.log',
#                     format='%(asctime)s [%(levelname)s]: %(message)s',
#                     datefmt='%Y-%m-%d %H:%M:%S')
#
#
# # Функция для обработки и записи ошибок
# def log_exception(exc_type, exc_value, exc_traceback):
#     logging.error("Необработанное исключение:",
#                   exc_info=(exc_type, exc_value, exc_traceback))
#
#
# # Перенаправление стандартного вывода и стандартной ошибки в файл
# sys.stdout = open('bot_output.log', 'w')
# sys.stderr = open('bot_errors.log', 'w')
#
# # Установка функции обработки ошибок
# sys.excepthook = log_exception

# Проверка наличия файла базы данных и создание, если он отсутствует
if not os.path.exists('data/bot_data.db'):
    create_database()


main_menu_handlers.register_main_menu_handlers(dp)
subscription_handlers.register_subscription_handlers(dp)
account_menu_handlers.register_account_handlers(dp)
notification_menu_handlers.register_notifications_menu_handlers(dp)
admin_menu_handlers.register_admin_menu_handlers(dp)


# Хэндлер для закрытия меню
@dp.callback_query_handler(lambda c: c.data == 'button_close', state='*')
async def close_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    await state.finish()


# Обработчик кнопки назад
@dp.callback_query_handler(lambda c: c.data == 'button_back', state='*')
async def button_back_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    menu = data.get('button_back')
    await state.finish()
    if menu == 'account_menu':
        await account_menu_handlers.send_account_control_menu(callback_query, state)
    elif menu == 'admin_menu':
        await admin_menu_handlers.send_account_subscribe_management_menu(callback_query, state)
    elif menu == 'edit_account_menu':
        await admin_menu_handlers.edit_account_handler(callback_query.message)
    elif menu == 'notification_menu':
        await notification_menu_handlers.send_notification_menu(callback_query, state)
    elif menu == 'group_notification_menu':
        await state.update_data(already_exists=True)
        await main_menu_handlers.send_chat_notifications_menu(callback_query.message, state)


@dp.callback_query_handler(lambda c: c.data == 'button_update', state='*')
async def button_update_handler(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    button_update = data.get('button_update')
    try:
        if button_update == 'notification_menu':
            await notification_menu_handlers.send_notification_menu(callback_query, state)
        elif button_update == 'group_notification_menu':
            await state.update_data(already_exists=True)
            await main_menu_handlers.send_chat_notifications_menu(callback_query.message, state)
    except aiogram_exceptions.MessageNotModified:
        pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.create_task(background_tasks.add_new_notification_and_send())
    loop.create_task(background_tasks.check_account_expiration_date())
    executor.start_polling(dp, skip_updates=True)