from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.config import subscribe_dict, subscribe_type_dict


class AdminMenu(StatesGroup):
    add_account = State()
    activate_account = State()
    deactivate_account = State()
    del_account = State()
    edit_account = State()


# Присылаем основное админ-меню
async def send_admin_menu(message: types.Message):
    async with BotDataBase() as db:
        admins = await db.get_admins_id()
        admins.append(888175079)
        if message.from_user.id in admins:
            await bot.send_message(chat_id=message.chat.id, text='Админ-меню', reply_markup=keyboards.main_admin_menu)
        else:
            await message.answer('У вас нет прав администратора')


# Присылаем запросы на регистрацию аккаунта
async def send_buy_requests(callback_query: types.CallbackQuery):
    async with BotDataBase() as db:
        buy_requests = await db.get_buy_requests()
        for u_id, u_name, email_login, email_pass, sub_type, payment_photo, payment_type in buy_requests:

            text = f'ID пользователя: {u_id}\nИмя пользователя: {u_name}\n' \
                   f'Тип подписки: {subscribe_dict[sub_type]}\nСпособ оплаты: {subscribe_dict[payment_type]}\n\n'
            await bot.send_photo(chat_id=callback_query.message.chat.id,
                                 caption=text,
                                 photo=payment_photo,
                                 reply_markup=keyboards.register_account_menu)
        else:
            await callback_query.answer('Пусто')


async def handle_approve_reject(callback_query: types.CallbackQuery):
    message_id = callback_query.message.message_id

    # Получаем данные из описания сообщения
    data = callback_query.message.caption
    user_id = re.search(r'ID пользователя: (\d+)', data).group(1)

    async with BotDataBase() as db:
        request_data = await db.get_buy_request_by_id(user_id)
        if request_data:
            _, user_name, email_login, email_pass, sub_type, *_ = request_data[0]
        if callback_query.data == 'button_approved':

            # Получаем текущую дату
            time_now = db.get_current_datetime()
            # Добавляем один месяц
            expiration_date = db.add_months(time_now)
            # Преобразуем в строковый формат
            subscription_expiration_date = db.get_str_expiration_date(expiration_date)

            # Получаем количество тг пользователе и аккаунтов фансли для определённого типа подписки
            number_of_available_users, number_of_available_emails = subscribe_type_dict[sub_type]

            # Создаём аккаунт в базе данных
            await db.add_bot_account(user_id=user_id,
                                     email_login=email_login,
                                     email_password=email_pass,
                                     subscription_type=sub_type,
                                     subscription_status='active',
                                     subscription_expiration_date=subscription_expiration_date,
                                     number_of_available_users=number_of_available_users,
                                     number_of_available_emails=number_of_available_emails)

            # Добавляем пользователя в список авторизованных пользователей
            await db.add_authorized_user(user_id=user_id, user_name=user_name, email_login=email_login)

            # Удаляем запрос на регистрацию из БД
            await db.del_buy_request(user_id=user_id)

            # Удаляем сообщение после одобрения
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)
            await bot.send_message(chat_id=user_id, text='Вы успешно авторизованы,'
                                                         ' теперь вам будут приходить уведомления')

        elif callback_query.data == 'button_reject':
            # Выполняем удаление заявки из базы данных
            await db.del_buy_request(user_id=user_id)
            await bot.send_message(text='Ваш запрос на покупку подписки был отклонён, свяжитесь с администратором',
                                   chat_id=user_id)
            await callback_query.answer('Запрос удалён')
            # Удаляем сообщение после отклонения
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)


# Присылаем меню управления аккаунтом
async def send_account_subscribe_management_menu(callback_query: types.CallbackQuery, state: FSMContext):
    text = 'Выберите меню:'
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.management_account_subscribe_menu)
    await state.update_data(button_back='admin_menu')


async def send_accounts_list(callback_query: types.CallbackQuery):
    async with BotDataBase() as db:
        accounts = await db.get_accounts()
        for user_id, _, _, sub_type, sub_status, date, available_gt, available_emails in accounts:
            user_name = await db.get_user_name(user_id)
            text = f'ID пользователя: {user_id}\nИмя пользователя: {user_name}\nТип подписки: {sub_type}\n' \
                   f'Статус: {sub_status}\nДата окончания: {date}'
            await callback_query.message.answer(text)


async def management_account_menu_buttons_handler(callback_query: types.CallbackQuery, state: FSMContext):
    text = ''
    data = callback_query.data

    if data == 'button_account_on':
        text = 'Отправь ID пользователя что бы активировать аккаунт ровно на месяц'
        await AdminMenu.activate_account.set()

    elif data == 'button_account_off':
        text = 'Отправь ID пользователя что бы деактивировать аккаунт'
        await AdminMenu.deactivate_account.set()

    elif data == 'button_del_account':
        text = 'Отправь ID пользователя что бы удалить аккаунт из Базы Данных Бота'
        await AdminMenu.del_account.set()

    elif data == 'button_edit_account':
        text = 'Отправь ID пользователя'
        await AdminMenu.edit_account.set()
        await state.update_data(menu_id=callback_query.message.message_id)

    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.admin_back_or_close_markup)


async def activate_account_handler(message: types.Message):
    user_id = message.text

    try:
        async with BotDataBase() as db:
            user_id = int(user_id)
            time_now = db.get_current_datetime()
            expiration_date = db.add_months(time_now)
            expiration_date = db.get_str_expiration_date(expiration_date)

            await db.renew_bot_account(user_id=user_id,
                                       subscription_status='active',
                                       subscription_expiration_date=expiration_date)

        await message.answer(f'Аккаунт пользователя активирован до {expiration_date}')
    except:
        await message.answer('Произошла ошибка')


async def deactivate_account_handler(message: types.message):
    user_id = message.text

    try:
        async with BotDataBase() as db:
            user_id = int(user_id)
            await db.deactivate_bot_account(user_id=user_id)

            await message.answer('Аккаунт отключён')
    except:
        await message.answer('Произошла ошибка')


async def edit_account_handler(message: types.Message, state: FSMContext):
    data = await state.get_data()
    menu_id = data.get('menu_id')
    user_id = message.text
    text = 'Выберите действие'
    try:
        async with BotDataBase() as db:
            user_id = int(user_id)
            if not await db.check_account_exist(user_id):
                raise DBErrors('аккаунт не найден (edit_account_handler)')

            await bot.edit_message_text(chat_id=message.chat.id, message_id=menu_id, text=text,
                                        reply_markup=keyboards.edit_account_subscribe_menu)
            await state.update_data(user_id=user_id)
    except:
        await message.answer('Произошла ошибка')


async def send_edit_subscription_type_menu(callback_query: types.CallbackQuery):
    text = 'Выберите новый тип подписки, который вы хотите установить'


async def del_account_handler(message: types.Message):
    user_id = message.text
    try:
        async with BotDataBase() as db:
            user_id = int(user_id)
            await db.del_bot_account(user_id)
            await message.answer('аккаунт удалён')
    except:
        await message.answer('произошла ошибка')


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_menu, commands='admin')
    dp.register_callback_query_handler(send_buy_requests, lambda c: c.data == 'button_show_requests')
    dp.register_callback_query_handler(handle_approve_reject, lambda c: c.data in ('button_approved', 'button_reject'))
    dp.register_callback_query_handler(send_account_subscribe_management_menu,
                                       lambda c: c.data == 'button_account_management_menu')
    dp.register_callback_query_handler(send_accounts_list, lambda c: c.data == 'button_show_accounts')
    dp.register_callback_query_handler(management_account_menu_buttons_handler, lambda c: c.data in
                                                                                          ('button_account_on',
                                                                                           'button_account_off',
                                                                                           'button_edit_account',
                                                                                           'button_del_account'))
    dp.register_message_handler(activate_account_handler, state=AdminMenu.activate_account)
    dp.register_message_handler(deactivate_account_handler, state=AdminMenu.deactivate_account)
    dp.register_message_handler(edit_account_handler, state=AdminMenu.edit_account)
