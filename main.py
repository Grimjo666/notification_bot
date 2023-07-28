import logging
import asyncio
import os

import sys
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
import aiogram.utils.exceptions as aiogram_exceptions


from bot.services.imap_control import get_new_message
from bot.config import EMAIL_PASS, EMAIL_USERNAME

from bot.create_bot import dp, bot
from bot.handlers import main_menu_handlers, subscription_handlers
from data.create_db import create_database
from bot.utils import keyboards

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

# @dp.message_handler(commands=['start', 'menu'])
# async def command_admin_menu(message: types.Message):
#     match message.chat.type, message.from_user.id:
#         case _, 888175079 | 491324681 | 1452171281:
#             await bot.send_message(chat_id=message.chat.id,
#                                    text='Админ-меню (расширенное):',
#                                    reply_markup=keyboards.main_menu)
#
#             # Добавляем группу\канал в систему уведомлений
#             if message.chat.type in ('group', 'supergroup', 'channel'):
#                 if not db_control.check_user_access(message.chat.id):
#                     db_control.add_user(user_id=message.chat.id,
#                                         username=message.chat.title)
#
#         case 'private', _:
#             await bot.send_message(chat_id=message.chat.id,
#                                    text='Админ-меню:',
#                                    reply_markup=keyboards.admin_menu)


@dp.message_handler(commands='test')
async def test(message: types):
    raise Exception("Тестовая ошибка")


# async def check_messages_background_task():
#     while True:
#         messages = get_new_message(username=EMAIL_USERNAME, mail_pass=EMAIL_PASS)
#         if len(messages) > 0:
#             for subject, recipient, text in messages:
#                 model_name = None
#                 try:
#                     model_name = db_control.get_email_name(recipient)[0]
#                 except:
#                     pass
#                 if model_name:
#                     text = f'---\nМодель: {model_name}\n\nТема: {subject}\n---'
#                 else:
#                     text = f'Модель: {recipient}\n\nТема: {subject}\n\n'
#
#                 for user in db_control.get_all_users():
#                     # Проверяем фильтр уведомлений пользователя
#                     if db_control.check_user_email_notification(user_id=user[0],
#                                                                 email=recipient.strip()):
#                         try:
#                             await bot.send_message(chat_id=user[0], text=text)
#                         except aiogram_exceptions.RetryAfter as e:
#                             await asyncio.sleep(e.timeout)
#                             await bot.send_message(chat_id=user[0], text=text)
#
#         await asyncio.sleep(30)


# Хэндлер для закрытия меню
@dp.callback_query_handler(lambda c: c.data == 'button_close', state='*')
async def close_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'button_main_menu', state='*')
async def send_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    match callback_query.message.chat.type, callback_query.from_user.id:
        case _, 888175079 | 491324681 | 1452171281:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text='Админ-меню (расширенное):',
                                        reply_markup=keyboards.main_menu)

        case 'private', _:
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text='Админ-меню:',
                                        reply_markup=keyboards.admin_menu)

    await state.finish()

if __name__ == '__main__':
    # loop = asyncio.get_event_loop()
    #
    # loop.create_task(check_messages_background_task())
    executor.start_polling(dp, skip_updates=True)