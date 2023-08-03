from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


from bot.models.bot_database_control import BotDataBase
from bot.utils import keyboards
from bot.create_bot import bot


class AccountMenu(StatesGroup):
    edit_notification_name = State()
    get_notification_name = State()


async def send_notification_and_transition_account_menu(callback_query: types.CallbackQuery):
    db = BotDataBase()
    user_id = callback_query.from_user.id
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    match db.check_account_exist(user_id), db.check_user_exist(user_id):
        case True, True:
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text='Выберите меню:',
                                        reply_markup=keyboards.transition_account_menu)

        case False, True:
            await bot.edit_message_text(chat_id=chat_id,
                                        message_id=message_id,
                                        text='Меню управления вашими личными уведомлениями:',
                                        reply_markup=keyboards.notification_menu)
        case False, False:
            await bot.send_message(chat_id=chat_id, text='У вас нет доступа к боту, купите/продлите подписку.')
    db.close()


async def send_account_control_menu(callback_query: types.CallbackQuery):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    text = 'Меню управления вашим аккаунтом\n\n'
    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text,
                                reply_markup=keyboards.account_menu)


async def send_notification_menu(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    db = BotDataBase()
    email_login = db.get_email_login_by_user_id(user_id=user_id)
    notifications = db.get_account_notifications(email_login=email_login)

    text = 'Меню управления вашими личными уведомлениями\n\nВсе ваши уведомления:\n\n'

    notifications_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)

    if len(notifications) == 0:
        text += 'У вас нет уведомлений'

    for _, email_recipient, notification_name, _ in notifications:
        if notification_name == 'None':
            notification_name = 'Не задано'
        text += f'--{email_recipient} | {notification_name}\n'
        notifications_keyboard.add(KeyboardButton(f'{email_recipient} | {notification_name}'))

    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text,
                                reply_markup=keyboards.notification_menu)

    await state.update_data(notifications_keyboard=notifications_keyboard, email_login=email_login)


async def requests_notification_name_for_change(callback_query: types.callback_query, state: FSMContext):
    chat_id = callback_query.message.chat.id

    data = await state.get_data()

    text = 'Выберите уведомление, имя которого хотите изменить'

    notifications_keyboard = data.get('notifications_keyboard')

    await bot.send_message(chat_id=chat_id,
                           text=text,
                           reply_markup=notifications_keyboard)

    await AccountMenu.edit_notification_name.set()


async def response_notification_name(message: types.Message, state: FSMContext):
    db = BotDataBase()
    data = await state.get_data()
    email_recipient = message.text.split()[0]
    email_login = data.get('email_login')

    notification_id = db.get_notification_id(email_login=email_login, email_recipient=email_recipient)
    if notification_id:
        await message.answer('Теперь отправьте имя')
        await state.update_data(notification_id=notification_id, message_id=message.message_id)
        await AccountMenu.get_notification_name.set()

    else:
        await message.answer('Произошла ошибка')
    db.close()


async def edit_notification_name(message: types.Message, state: FSMContext):
    db = BotDataBase()
    data = await state.get_data()
    notification_id = data.get('notification_id')
    message_id = data.get('message_id')

    db.edit_account_notification_name(notification_id=notification_id, notification_name=message.text)
    await message.answer('Имя успешно изменено')

    await bot.delete_message(chat_id=message.chat.id, message_id=message_id)
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    await state.finish()
    db.close()


def register_account_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_notification_and_transition_account_menu,
                                       lambda c: c.data == 'button_account_menu')
    dp.register_callback_query_handler(send_account_control_menu, lambda c: c.data == 'button_account_menu_control')
    dp.register_callback_query_handler(send_notification_menu, lambda c: c.data == 'button_notification_menu')
    dp.register_callback_query_handler(requests_notification_name_for_change, lambda c: c.data == 'button_edit_notification_name')
    dp.register_message_handler(response_notification_name, state=AccountMenu.edit_notification_name)
    dp.register_message_handler(edit_notification_name, state=AccountMenu.get_notification_name)