import logging
import asyncio
import os
from aiogram import executor, types
from aiogram.dispatcher import FSMContext
from bot.services.imap_control import get_new_message
from bot.config import EMAIL_PASS, EMAIL_USERNAME

from bot.create_bot import dp, bot
from bot.handlers.admin_handlers import register_main_admin_handlers
from bot.handlers.notification_handlers import register_notification_handlers
from bot.utils.keyboards import main_admin_menu
from data.create_db import create_database
from bot.services import db_control
from bot.utils import keyboards

logging.basicConfig(level=logging.INFO)

# Проверка наличия файла базы данных и создание, если он отсутствует
if not os.path.exists('data/bot_data.db'):
    create_database()


register_main_admin_handlers(dp)
register_notification_handlers(dp)


@dp.message_handler(commands=['start', 'menu'])
async def command_admin_menu(message: types.Message):
    match message.chat.type, message.from_user.id:
        case _, 888175079 | 491324681 | 1452171281:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Админ-меню (расширенное):',
                                   reply_markup=keyboards.main_admin_menu)

            # Добавляем группу\канал в систему уведомлений
            if message.chat.type in ('group', 'supergroup', 'channel'):
                db_control.add_user(user_id=message.chat.id,
                                    username=message.chat.title)

        case 'private', _:
            await bot.send_message(chat_id=message.chat.id,
                                   text='Админ-меню:',
                                   reply_markup=keyboards.admin_menu)


async def check_messages_background_task():
    while True:
        messages = get_new_message(username=EMAIL_USERNAME, mail_pass=EMAIL_PASS)
        if len(messages) > 0:
            for subject, recipient, text in messages:
                text = f'Модель: {recipient}\nТема: {subject}\n\n{text}'

                for user in db_control.get_all_users():

                    # Проверяем фильтр уведомлений пользователя
                    if db_control.check_user_model_notification(user_id=user[0],
                                                                model_email=recipient.strip()):
                        await bot.send_message(chat_id=user[0], text=text)

        await asyncio.sleep(60)


# Хэндлер для закрытия меню
@dp.callback_query_handler(lambda c: c.data == 'button_close', state='*')
async def close_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(chat_id=callback_query.message.chat.id,
                             message_id=callback_query.message.message_id)

    await state.finish()


@dp.callback_query_handler(lambda c: c.data == 'button_main_menu', state='*')
async def send_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Админ-меню:',
                                reply_markup=main_admin_menu)

    await state.finish()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(check_messages_background_task())
    executor.start_polling(dp, skip_updates=True)