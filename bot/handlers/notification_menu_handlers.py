from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import logging

from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.utils import keyboards
from bot.create_bot import bot


class NotificationsMenu(StatesGroup):
    switch_notification = State()


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
        filters = await db.get_filters_notifications(user_id=user_id)
        text_filters = 'Уведомления:\n'
        filter_names = ['сообщения', 'покупки', 'остальные']

        for filter_value, filter_name in zip(filters, filter_names):
            status = 'включены' if filter_value == 1 else 'выключены'
            text_filters += f'-{filter_name} - {status}\n'

        text = f'Меню управления вашими личными уведомлениями\n\n {text_filters}\n\nВсе ваши уведомления:\n\n'

        notifications_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)

        if len(notifications) == 0:
            text += 'У вас нет уведомлений'

        for notification_id, email_recipient, notification_name, _ in notifications:
            mode = 'Включено'
            if notification_name == 'None':
                notification_name = 'Не задано'
            if await db.check_user_notification_filtered(user_id=user_id, notification_id=notification_id):
                mode = 'Выключено'

            notifications_keyboard.add(KeyboardButton(f'{email_recipient} | {notification_name} - {mode}'))
            text += f'--{email_recipient} | {notification_name} - {mode}\n'

        await bot.edit_message_text(chat_id=chat_id,
                                    message_id=message_id,
                                    text=text,
                                    reply_markup=keyboards.notification_menu)

        await state.update_data(notifications_keyboard=notifications_keyboard,
                                email_login=email_login,
                                notification_menu_id=callback_query.message.message_id)
        await state.update_data(button_update='notification_menu', button_back='notification_menu')


async def send_switch_notifications_buttons(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    keyboard = data.get('notifications_keyboard')

    await callback_query.message.answer(text='Выберите уведомление что бы переключить его', reply_markup=keyboard)
    await NotificationsMenu.switch_notification.set()


async def switch_notification_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email_login = data.get('email_login')
    notification_menu_id = data.get('notification_menu_id')
    email_recipient, *_ = message.text.split(' | ')

    async with BotDataBase() as db:
        notification_id = await db.get_notification_id(email_login=email_login,
                                                       email_recipient=email_recipient)

        # переключаем уведомление
        await db.switch_user_notification(user_id=message.from_user.id,
                                          notification_id=notification_id)
    await message.answer('Переключено')


async def send_switch_notification_filters_menu(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Выберите кнопку для того что бы включить/отключить уведомления определённого типа',
                                reply_markup=keyboards.switch_notification_filters_menu)


async def switch_filters(callback_query: types.CallbackQuery):
    callback_data = callback_query.data
    user_id = callback_query.from_user.id
    async with BotDataBase() as db:
        filters = await db.get_filters_notifications(user_id)
        try:
            if filters is False:
                raise DBErrors('У пользователя нет фильтров (switch_notifications)')

            message_filter, purchase_filter, other_filter = filters

            if callback_data == 'button_message_filter':
                message_filter = int(not message_filter)

            elif callback_data == 'button_paid_filter':
                purchase_filter = int(not purchase_filter)

            elif callback_data == 'button_other_filter':
                other_filter = int(not other_filter)

            await db.switch_filters_notifications(user_id=user_id,
                                                  message_notifications=message_filter,
                                                  purchase_notifications=purchase_filter,
                                                  other_notifications=other_filter)

            await callback_query.answer('Фильтр переключён')
        except DBErrors as ex:
            print(ex)


def register_notifications_menu_handlers(dp: Dispatcher):
    try:
        dp.register_callback_query_handler(send_notification_menu, lambda c: c.data == 'button_notification_menu')
        dp.register_callback_query_handler(send_switch_notifications_buttons, lambda c: c.data == 'button_switch_notifications')
        dp.register_message_handler(switch_notification_handler, state=NotificationsMenu.switch_notification)
        dp.register_callback_query_handler(send_switch_notification_filters_menu,
                                           lambda c: c.data == 'button_add_filters', state='*')
        dp.register_callback_query_handler(switch_filters, lambda c: c.data in ('button_message_filter',
                                                                                'button_paid_filter',
                                                                                'button_other_filter'), state='*')
    except Exception as ex:
        logging.error(f"Error while registering notifications menu handlers: {ex}")