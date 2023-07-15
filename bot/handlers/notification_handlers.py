from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from bot.utils import keyboards
from bot.create_bot import bot
from bot.services import db_control
from bot.handlers.admin_handlers import AdminMenuState


async def add_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Выберите модель для добавления оповещения',
                                reply_markup=keyboards.notification_menu)
    await AdminMenuState.add_notification.set()
    await state.update_data(add_notification_menu_id=callback_query.message.message_id)


async def add_notification_for_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('add_notification_menu_id')

    user_access = db_control.check_user_access(message.from_user.id)
    model = message.text.replace('/', '').split()
    model_email = model[0]
    model_name = ' '.join(model[1:])

    if user_access:
        if len(model) < 3:
            db_control.set_user_model_notification(message.from_user.id, model_email)
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=message_id,
                                        text='Выберите модель для добавления оповещения\n\n'
                                             f'Оповещение о {model_name} добавлено',
                                        reply_markup=keyboards.notification_menu)
        else:
            await message.answer('Не корректные данные')
    else:
        await message.answer('У вас нет доступа')


async def del_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Выберите модель для удаления оповещения',
                                reply_markup=keyboards.del_notification_menu)

    await AdminMenuState.del_notification.set()
    await state.update_data(del_notification_menu_id=callback_query.message.message_id)


async def del_notification_for_user(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('del_notification_menu_id')
    model = message.text.split()
    model_name = " ".join(model[1:]).replace("/", "")

    if db_control.check_user_model_notification(user_id=message.from_user.id, model_email=model[0]):
        access_id = db_control.get_user_model_notification_id(user_id=message.from_user.id, model_email=model[0])

        db_control.del_user_model_notification(access_id)

        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Выберите модель для удаления оповещения\n\n'
                                         f'Оповещение о {model_name} удалено',
                                    reply_markup=keyboards.del_notification_menu)


async def add_all_models_notification(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    models = db_control.get_all_models()

    for model in models:
        model_email = model[0]
        db_control.set_user_model_notification(user_id, model_email)

    await callback_query.answer('Все уведомления добавлены')


async def show_activ_notification(callback_query: types.CallbackQuery):
    user_id = callback_query.message.chat.id
    user_notifications = keyboards.create_notification_keyboard(user_id)
    text = 'Активные уведомления:\n\n'

    if user_notifications:
        await callback_query.message.answer('Выберите уведомление, которое хотите удалить:',
                                            reply_markup=user_notifications)
    else:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text='Нет активных уведомлений',
                                    reply_markup=keyboards.close_menu)


def register_notification_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(add_notification_menu,
                                       lambda c: c.data == 'button_add_notification_menu')
    dp.register_message_handler(add_notification_for_user,
                                state=AdminMenuState.add_notification)
    dp.register_callback_query_handler(del_notification_menu,
                                       lambda c: c.data == 'button_del_notification_menu')
    dp.register_message_handler(del_notification_for_user,
                                state=AdminMenuState.del_notification)
    dp.register_callback_query_handler(add_all_models_notification,
                                       lambda c: c.data == 'button_add_all_notification',
                                       state='*')
    dp.register_callback_query_handler(show_activ_notification,
                                       lambda c: c.data == 'button_your_notification',
                                       state='*')
