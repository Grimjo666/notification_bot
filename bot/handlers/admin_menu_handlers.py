from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase
from bot.config import subscribe_dict, subscribe_type_dict


class AdminMenu(StatesGroup):
    add_account = State()


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

            # Удаляем сообщение после одобрения
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)
            await bot.send_message(chat_id=user_id, text='Вы успешно авторизованы,'
                                                         ' теперь вам будут приходить уведомления')
            await callback_query.answer('Пользователь зарегистрирован')
        elif callback_query.data == 'button_reject':
            # Выполняем удаление заявки из базы данных
            await callback_query.answer('Запрос удалён')
            # Удаляем сообщение после отклонения
            await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=message_id)


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(send_admin_menu, commands='admin')
    dp.register_callback_query_handler(send_buy_requests, lambda c: c.data == 'button_show_requests')
    dp.register_callback_query_handler(handle_approve_reject, lambda c: c.data in ('button_approved', 'button_reject'))


