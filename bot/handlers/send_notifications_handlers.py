# from aiogram import types, Dispatcher
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters.state import State, StatesGroup
# import aiogram.utils.exceptions as aiogram_exceptions
#
#
# from bot.services.imap_control import get_new_message
# from bot.config import EMAIL_PASS, EMAIL_USERNAME
# from bot.utils import keyboards
# from bot.create_bot import bot
# from bot.models.bot_database_control import BotDataBase
#
#
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


import imaplib
import email
from bot import config
from email.header import decode_header


def get_email_recipients(email_address, password, imap_server='imap.example.com', port=993, ssl=True):
    recipients = []

    imap_server = config.IMAP_SERVER

    # Подключение к серверу IMAP
    imap = imaplib.IMAP4_SSL(imap_server)
    imap.login(email_address, password)

    try:
        # Подключаемся к IMAP-серверу
        if ssl:
            imap = imaplib.IMAP4_SSL(imap_server, port)
        else:
            imap = imaplib.IMAP4(imap_server, port)

        # Логинимся в учетной записи
        imap.login(email_address, password)

        # Выбираем папку с письмами (INBOX)
        imap.select('INBOX')

        # Ищем все письма без их фактического чтения
        _, msg_ids = imap.search(None, 'UNSEEN')
        msg_ids = msg_ids[0].split()

        for msg_id in msg_ids:
            # Получаем заголовок сообщения без чтения всего письма
            _, msg_data = imap.fetch(msg_id, '(BODY.PEEK[HEADER])')
            msg = email.message_from_bytes(msg_data[0][1])

            # Получаем информацию о получателе (адрес email)
            recipients.append(msg.get('To'))

        # Закрываем подключение
        imap.logout()

    except Exception as e:
        print(f"Произошла ошибка: {e}")

    return recipients


print(get_email_recipients(config.EMAIL_USERNAME, config.EMAIL_PASS))
