from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.utils import keyboards
from bot.create_bot import bot
from bot.services import db_control
from bot.handlers.admin_handlers import AdminMenuState
from data.create_db import create_table_notifications


async def add_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Выберите уведомление что-бы включить его',
                                reply_markup=keyboards.notification_menu)
    await AdminMenuState.notification_on.set()
    await state.update_data(add_notification_menu_id=callback_query.message.message_id)


async def add_notification_for_user(message: types.Message, state: FSMContext):
    create_table_notifications()

    user_id = message.chat.id

    data = await state.get_data()
    message_id = data.get('add_notification_menu_id')

    user_access = db_control.check_user_access(user_id)
    model = message.text.replace('/', '').split()
    model_email = model[0]
    model_name = ' '.join(model[1:])

    if user_access:
        db_control.set_user_email_notification(user_id, model_email)
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Выберите уведомление что-бы включить его\n\n'
                                         f'Уведомление о {model_name} включено',
                                    reply_markup=keyboards.notification_menu)
    else:
        await message.answer('У вас нет доступа')


async def del_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    notifications = db_control.get_all_user_email_notification(callback_query.message.chat.id)
    text = 'Выберите уведомление для отключения\n\n'
    if notifications:
        for ntf in notifications:
            text += f'-- {db_control.get_email_name(ntf[0])[0]}\n'

    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.del_notification_menu)

    await AdminMenuState.notification_off.set()
    await state.update_data(del_notification_menu_id=callback_query.message.message_id)


async def del_notification_for_user(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    data = await state.get_data()
    message_id = data.get('del_notification_menu_id')
    model = message.text.split()
    model_name = " ".join(model[1:]).replace("/", "")

    if db_control.check_user_email_notification(user_id=user_id, email=model[0]):
        access_id = db_control.get_user_email_notification_id(user_id=user_id, email=model[0])

        db_control.del_user_email_notification(access_id)

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Выберите Уведомление для удаления\n\n'
                                         f'Уведомление о {model_name} выключено',
                                    reply_markup=keyboards.del_notification_menu)


async def add_all_emails_notification(callback_query: types.CallbackQuery):
    create_table_notifications()
    user_id = callback_query.message.chat.id

    models = db_control.get_all_emails()

    for model in models:
        model_email = model[0]
        db_control.set_user_email_notification(user_id, model_email)

    await callback_query.answer('Все уведомления добавлены')


async def show_activ_notification(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    user_notifications = keyboards.create_notification_keyboard(user_id)

    if user_notifications:
        await callback_query.message.answer('Выберите уведомление, которое хотите удалить:',
                                            reply_markup=user_notifications)
    else:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Нет активных уведомлений',
                                    reply_markup=keyboards.close_menu)


async def off_all_notification(callback_query: types.CallbackQuery):
    db_control.del_all_user_email_notifications(callback_query.message.chat.id)
    await callback_query.answer('Все уведомления отключены')


def register_notification_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(add_notification_menu,
                                       lambda c: c.data == 'button_add_notification_menu')
    dp.register_message_handler(add_notification_for_user,
                                state=AdminMenuState.notification_on)
    dp.register_callback_query_handler(del_notification_menu,
                                       lambda c: c.data == 'button_del_notification_menu')
    dp.register_message_handler(del_notification_for_user,
                                state=AdminMenuState.notification_off)
    dp.register_callback_query_handler(add_all_emails_notification,
                                       lambda c: c.data == 'button_add_all_notification',
                                       state='*')
    dp.register_callback_query_handler(show_activ_notification,
                                       lambda c: c.data == 'button_your_notification',
                                       state='*')
    dp.register_callback_query_handler(off_all_notification, lambda c: c.data == 'button_del_all_notification',
                                       state=AdminMenuState.notification_off)