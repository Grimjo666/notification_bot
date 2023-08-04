from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from sqlite3 import IntegrityError


from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.utils import keyboards
from bot.create_bot import bot


class AccountMenu(StatesGroup):
    edit_notification_name = State()
    get_notification_name = State()
    add_user = State()
    del_user = State()


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


async def send_account_control_menu(callback_query: types.CallbackQuery, state: FSMContext):
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id
    user_id = callback_query.from_user.id

    db = BotDataBase()
    email_login = db.get_email_login_by_user_id(user_id=user_id)
    notifications = db.get_account_notifications(email_login=email_login)
    users = db.get_users_from_authorized_users(email_login=email_login)

    text = 'Меню управления вашим аккаунтом\n\nУведомления аккаунта:\n'

    notifications_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)
    users_keyboard = ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=False)

    if len(notifications) == 0:
        text += 'У вас нет уведомлений'

    for _, email_recipient, notification_name, _ in notifications:
        if notification_name == 'None':
            notification_name = 'Не задано'
        text += f'--{email_recipient} | {notification_name}\n'
        notifications_keyboard.add(KeyboardButton(f'{email_recipient} | {notification_name}'))

    text += '\nПользователи с доступом к боту:\n'

    for db_user_id, user_name, _, _, _, is_chat, _ in users:
        if db_user_id == user_id:
            text += f'--{user_name} <- ВЫ\n'
        else:
            text += f'--{user_name}\n'
            users_keyboard.add(KeyboardButton(f'{db_user_id} | {user_name}'))

    await bot.edit_message_text(chat_id=chat_id,
                                message_id=message_id,
                                text=text,
                                reply_markup=keyboards.account_menu)

    await state.update_data(notifications_keyboard=notifications_keyboard,
                            users_keyboard=users_keyboard,
                            email_login=email_login)
    db.close()


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


# Добавляем доступ для пользователя к уведомлениям аккаунта
async def add_user_to_account_menu(callback_query: types.CallbackQuery):
    text = 'Введите ID пользователя, для которого вы хотите дать доступ к уведомлениям вашего аккаунта\n\n' \
           'Для того что бы узнать ID нужно что бы этот пользователь написал боту /start и нажал на кнопку ' \
           '"Узнать свой ID", после этого попросите его сказать свой ID вам и отправьте его сообщением в этом меню'

    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.back_or_close_menu)
    await AccountMenu.add_user.set()


async def add_user_to_account(message: types.Message, state: FSMContext):
    user_id_add_access = message.text.strip()
    await bot.delete_message(message_id=message.message_id, chat_id=message.chat.id)

    if user_id_add_access.isdigit():
        db = BotDataBase()
        try:
            data = await state.get_data()
            email_login = data.get('email_login')
            user_info = await bot.get_chat(user_id_add_access)
            user_name = user_info.full_name
            db.add_authorized_user(user_id=user_id_add_access,
                                   user_name=user_name,
                                   email_login=email_login)
            await message.answer('Пользователь добавлен')
        except DBErrors as ex:
            await message.answer(ex)
        except IntegrityError as ex:
            await message.answer('У этого пользователя уже есть доступ')
        except Exception as ex:
            print(type(ex), ex, 'Ошибка при добавлении нового пользователя')
            await message.answer('Произошла ошибка')
        finally:
            db.close()
    else:
        await message.answer('Не корректный ID')


async def del_user_from_account_menu(callback_query: types.CallbackQuery):
    text = 'Введите ID пользователя или выберите его на клавиатуре для того что бы убрать доступ к боту'
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.del_user_access_menu)
    await AccountMenu.del_user.set()


async def send_users_keyboard(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    users_keyboard = data.get('users_keyboard')

    await callback_query.message.answer(text='Выберите пользователя:', reply_markup=users_keyboard)


async def del_user_from_account(message: types.Message):
    db_user_id, *other = message.text.split()
    user_name = ''.join(other).replace('|', '')

    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    if not db_user_id.isdigit():
        await message.answer('Не корректный ID')
    elif db_user_id == message.from_user.id:
        await message.answer('Вы не можете удалить себя')
    else:
        db = BotDataBase()
        db.del_authorized_user(db_user_id)
        await message.answer(f'Пользователь {user_name} удалён')
        db.close()


async def button_back_account_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await send_account_control_menu(callback_query, state)
    await state.finish()


def register_account_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_notification_and_transition_account_menu,
                                       lambda c: c.data == 'button_account_menu')
    dp.register_callback_query_handler(send_account_control_menu, lambda c: c.data == 'button_account_menu_control')
    dp.register_callback_query_handler(requests_notification_name_for_change,
                                       lambda c: c.data == 'button_edit_notification_name')
    dp.register_message_handler(response_notification_name, state=AccountMenu.edit_notification_name)
    dp.register_message_handler(edit_notification_name, state=AccountMenu.get_notification_name)
    dp.register_callback_query_handler(add_user_to_account_menu, lambda c: c.data == 'button_add_user_to_account')
    dp.register_message_handler(add_user_to_account, state=AccountMenu.add_user)
    dp.register_callback_query_handler(del_user_from_account_menu, lambda c: c.data == 'button_del_user_from_account')
    dp.register_callback_query_handler(send_users_keyboard, lambda c: c.data == 'button_show_users', state='*')
    dp.register_message_handler(del_user_from_account, state=AccountMenu.del_user)
    dp.register_callback_query_handler(button_back_account_menu, lambda c: c.data == 'button_back', state='*')