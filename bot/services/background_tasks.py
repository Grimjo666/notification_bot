import asyncio
import aiogram.utils.exceptions as aiogram_exceptions

from bot.services.imap_control import subject_filter
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.services.imap_control import get_new_message


async def add_new_notification_and_send():
    """Это фоновая задача, которая проверяет новые уведомления с почт пользователей и отправляет их пользователям,
    если у них есть записи об уведомлениях. Если записей нет. то они добавляются в БД"""
    while True:
        async with BotDataBase() as db:
            for user_id, email_login, email_password, *_ in await db.get_accounts():
                # если подписка не активна, пропускаем аккаунт
                if not await db.check_subscription_status(user_id=user_id):
                    continue
                await asyncio.sleep(0.5)
                email_password = await db.decrypt_password(email_password)
                # получаем новые сообщения для зарегистрированного аккаунта
                messages = get_new_message(email_address=email_login, email_pass=email_password)
                account_users = await db.get_users_from_authorized_users(email_login=email_login)

                # Проходимся по сообщению пользователя
                for subject, recipient in messages:
                    notification_id = await db.get_notification_id(email_login=email_login,
                                                                   email_recipient=recipient)
                    # проходимся по пользователям бота
                    for authorized_user_id, user_name, messn, purchn, othn, is_chat, _ in account_users:
                        # Проверяем существует ли запись о уведомлении в аккаунте
                        if await db.check_notification_exist(notification_id):
                            # проверяем существует ли запись о уведомлении у пользователя
                            if await db.check_user_notification_exist(notification_id=notification_id,
                                                                      user_id=authorized_user_id):
                                # Применяем пользовательские фильтры к сообщениям
                                if subject_filter(subject, message_notifications=messn,
                                                  purchase_notifications=purchn,
                                                  other_notifications=othn):
                                    continue

                                if await db.check_user_notification_filtered(user_id=authorized_user_id,
                                                                             notification_id=notification_id):
                                    continue

                                # Получаем имя уведомления
                                notification_name = await db.get_notification_name(notification_id=notification_id)
                                if notification_name != 'None':
                                    recipient = notification_name

                                text = f'---\nАккаунт: {recipient}\nТема: {subject}\n---'

                                await send_message_with_delay(bot, authorized_user_id, text, delay_seconds=0.5)
                            # если записи о уведомлении нет у пользователя, добавляем её
                            else:
                                await db.add_notification_to_users_notifications(notification_id=notification_id,
                                                                                 user_id=authorized_user_id)
                        # Если записи о уведомлении нет в аккаунте, добавляем её
                        else:
                            try:
                                await db.add_account_notification(email_recipient=recipient, email_login=email_login)
                            except DBErrors as ex:
                                print(ex)

        await asyncio.sleep(20)


async def check_account_expiration_date():
    while True:
        async with BotDataBase() as  db:
            for user_id, _, _, _, subscription_status, subscription_expiration_date, *_ in await db.get_accounts():
                if not await db.check_subscription_status(user_id=user_id):
                    continue
                if not await db.check_expiration_date(subscription_expiration_date):
                    await db.deactivate_bot_account(user_id=user_id)
        await asyncio.sleep(300)


# отправка сообщения с установленной задержкой
async def send_message_with_delay(my_bot, user_id, text, delay_seconds):
    try:
        await asyncio.sleep(delay_seconds)
        await my_bot.send_message(chat_id=user_id, text=text)
    except aiogram_exceptions.RetryAfter as e:
        await asyncio.sleep(e.timeout)
        await send_message_with_delay(my_bot, user_id, text, delay_seconds)
