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


# Хэндлер для закрытия меню
@dp.callback_query_handler(lambda c: c.data == 'button_close', state='*')
async def close_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    await state.finish()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()

    loop.create_task(background_tasks.add_new_notification_and_send())
    executor.start_polling(dp, skip_updates=True)