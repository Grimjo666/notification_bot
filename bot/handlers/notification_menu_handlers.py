from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.models.bot_database_control import BotDataBase
from bot.utils import keyboards
from bot.create_bot import bot


async def send_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    """
    отправляем главное мню уведомлений, и создаём две клавиатуры(включённые уведомления, выключенные уведомления),
    в последствии передаём их в следующие меню
    """
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    async with BotDataBase() as db:
        email_login = await db.get_email_login_by_user_id(user_id=user_id)
        notifications = await db.get_account_notifications(email_login=email_login)

        text = 'Меню управления вашими личными уведомлениями\n\nВсе ваши уведомления:\n\n'

        notifications_keyboard_on = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
        notifications_keyboard_off = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)

        if len(notifications) == 0:
            text += 'У вас нет уведомлений'

        for notification_id, email_recipient, notification_name, _ in notifications:
            mode = 'Включено'
            if notification_name == 'None':
                notification_name = 'Не задано'
            if await db.check_user_notification_filtered(user_id=user_id, notification_id=notification_id):
                mode = 'Выключено'
                notifications_keyboard_off.add(KeyboardButton(f'{email_recipient} | {notification_name}'))
            else:
                notifications_keyboard_on.add(KeyboardButton(f'{email_recipient} | {notification_name}'))
            text += f'--{email_recipient} | {notification_name} - {mode}\n'

        await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text,
                                    reply_markup=keyboards.notification_menu)

        await state.update_data(notifications_keyboard_on=notifications_keyboard_on, email_login=email_login)


def register_notifications_menu_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_notification_menu, lambda c: c.data == 'button_notification_menu')
