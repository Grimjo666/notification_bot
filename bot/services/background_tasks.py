from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.utils import keyboards
from bot.create_bot import bot
from bot.handlers.admin_menu_handlers import AdminMenuState
from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.services.imap_control import get_new_message


# Функция для проверки почтовых ящиков и поиска и добавления новых уведомлений в аккаунт бота
async def add_new_notification_to_account():
    while True:
        db = BotDataBase()
        bot_accounts = db.get_accounts()
        # Проходимся по аккаунтам пользователей
        for _, email_address, account_password, *_ in bot_accounts:
            # Расшифровываем пароль
            account_password = db.decrypt_password(account_password)
            # Получаем список не прочитанных сообщений в почте email_address
            messages = get_new_message(email_address=email_address, email_pass=account_password)
            # Проходимся по списку сообщений
            for message in messages:
                recipient = message[1]
                try:
                    # добавляем уведомление в таблицу account_notification
                    db.add_account_notification(email_recipients=recipient,
                                                email_login=email_address)
                    # Получаем ID уведомления
                    notification_id = db.get_notification_id(email_login=email_address,
                                                             email_recipient=recipient)
                    # получаем user_id пользователей
                    users = db.get_users_from_authorized_users(email_login=email_address)
                    if users:
                        for user_id, *_ in users:
                            # Проверяем есть ли уведомление в списке уведомлений пользователя
                            if not db.check_user_notification_exist(notification_id=notification_id,
                                                                    user_id=user_id):
                                # Добавляем уведомление в таблицу уведомлений пользователя
                                db.add_notification_to_users_notifications(notification_id=notification_id,
                                                                           user_id=user_id)
        db.close()
                except DBErrors as ex:
                    pass


async def check_messages_background_task(messages):
    while True:
        if len(messages) > 0:
            for subject, recipient in messages:
                model_name = None

                if model_name:
                    text = f'---\nМодель: {model_name}\n\nТема: {subject}\n---'
                else:
                    text =  f'---\nМодель: {recipient}\n\nТема: {subject}\n---'

                for user in db_control.get_all_users():
                    # Проверяем фильтр уведомлений пользователя
                    if db_control.check_user_email_notification(user_id=user[0],
                                                                email=recipient.strip()):
                        try:
                            await bot.send_message(chat_id=user[0], text=text)
                        except aiogram_exceptions.RetryAfter as e:
                            await asyncio.sleep(e.timeout)
                            await bot.send_message(chat_id=user[0], text=text)

        await asyncio.sleep(30)

