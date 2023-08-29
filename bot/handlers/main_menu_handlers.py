from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import logging
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase


class MenuState(StatesGroup):
    pass


async def command_start(message: types.Message):
    text = "Привет! Я бот, созданный для отслеживания уведомлений с сайта Fansly. " \
           "Я могу помочь тебе получать оповещения с твоих аккаунтов Fansly." \
           "Бот может присылать уведомления сразу с большого количества аккаунтов\n" \
           "Вызвать это меню можно по команде /start, /menu\n\n\n" \
           "Выбери одну из следующих опций:\n\n" \
           "|Подписка| - здесь ты можешь купить или продлить свою подписку на меня\n\n" \
           "|Как настроить бота| - здесь вся информация по настройке бота\n\n" \
           "|Аккаунт| - управление твоим аккаунтом бота"
    await bot.send_message(text=text, chat_id=message.from_user.id, reply_markup=keyboards.main_menu)


async def send_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Привет! Я бот, созданный для отслеживания уведомлений с сайта Fansly. " \
           "Я могу помочь тебе получать оповещения с твоих аккаунтов Fansly. " \
           "Бот может присылать уведомления сразу с большого количества аккаунтов\n\n\n" \
           "Выбери одну из следующих опций:\n\n" \
           "|Подписка| - здесь ты можешь купить или продлить свою подписку на меня\n\n" \
           "|Как настроить бота| - здесь вся информация по настройке бота\n\n" \
           "|Аккаунт| - управление твоим аккаунтом бота"
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.main_menu)

    await state.finish()


async def send_chat_notifications_menu(message: types.Message, state: FSMContext):
    data = await state.get_data()
    already_exists = data.get('already_exists')
    user_id = message.chat.id

    async with BotDataBase() as db:
        email_login = await db.get_email_login_by_user_id(user_id=user_id)
        notifications = await db.get_account_notifications(email_login=email_login)
        filters = await db.get_filters_notifications(user_id=user_id)
        text_filters = 'Уведомления:\n'
        filter_names = ['сообщения', 'покупки', 'остальные']

        for filter_value, filter_name in zip(filters, filter_names):
            status = 'включены' if filter_value == 1 else 'выключены'
            text_filters += f'-{filter_name} - {status}\n'

        text = f'Меню управления уведомлениями чата\n\n {text_filters}\n\nВсе уведомления:\n\n'

        notifications_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)

        if len(notifications) == 0:
            text += 'Нет уведомлений'

        for notification_id, email_recipient, notification_name, _ in notifications:
            mode = 'Включено'
            if notification_name == 'None':
                notification_name = 'Не задано'
            if await db.check_user_notification_filtered(user_id=message.chat.id, notification_id=notification_id):
                mode = 'Выключено'

            notifications_keyboard.add(KeyboardButton(f'{email_recipient} | {notification_name} - {mode}'))
            text += f'--{email_recipient} | {notification_name} - {mode}\n'

        if await db.check_user_exist(message.chat.id):
            if not already_exists:
                await bot.send_message(chat_id=message.chat.id,
                                       text=text,
                                       reply_markup=keyboards.group_notifications_menu)
            else:
                await bot.edit_message_text(chat_id=message.chat.id,
                                            message_id=message.message_id,
                                            text=text,
                                            reply_markup=keyboards.group_notifications_menu)

            await state.update_data(notifications_keyboard=notifications_keyboard,
                                    email_login=email_login,
                                    notification_menu_id=message.message_id)
            await state.update_data(button_update='group_notification_menu', button_back='group_notification_menu')
        else:
            await message.answer('Этот чат не авторизован в боте')


async def send_user_id(callback_query: types.CallbackQuery):
    await callback_query.message.answer(f'Ваш ID: {callback_query.from_user.id}')


def register_main_menu_handlers(dp: Dispatcher):
    try:
        dp.register_message_handler(command_start, commands=['start', 'menu'])
        dp.register_callback_query_handler(send_main_menu, lambda c: c.data == 'button_main_menu', state='*')
        dp.register_callback_query_handler(send_user_id, lambda c: c.data == 'button_send_user_id', state='*')
        dp.register_message_handler(send_chat_notifications_menu, commands='chat_menu')
    except Exception as ex:
        logging.error(f"Error while registering main menu handlers: {ex}")