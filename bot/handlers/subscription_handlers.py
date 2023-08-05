from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase
from bot.services.imap_control import is_valid_imap_credentials


class SubscriptionMenu(StatesGroup):
    free_subscription = State()
    free_subscription_request_data = State()
    free_subscription_get_user_data = State()
    paid_subscription = State()
    paid_subscription_get_user_data = State()


async def send_payment_method_menu(callback_query: types.CallbackQuery, state: FSMContext):
    async with BotDataBase() as db:
        user_exist = await db.check_user_exist(callback_query.from_user.id)

        if not user_exist:
            text = 'Так как вы не разу ни пользовались ботом, вам доступна бесплатная пробная подписка на 2 дня'
            await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                        message_id=callback_query.message.message_id,
                                        text=text,
                                        reply_markup=keyboards.free_subscription_menu)
            await state.update_data(subscription_register_menu_id=callback_query.message.message_id)
        else:
            text = 'Выберите способ оплаты:'
            await bot.edit_message_text(message_id=callback_query.message.message_id,
                                        chat_id=callback_query.message.chat.id,
                                        text=text,
                                        reply_markup=keyboards.payment_method_menu)


async def skip_button_handler(callback_query: types.CallbackQuery):
    text = 'Выберите способ оплаты:'
    await bot.edit_message_text(message_id=callback_query.message.message_id,
                                chat_id=callback_query.message.chat.id,
                                text=text,
                                reply_markup=keyboards.payment_method_menu)


# Присылаем пользователю меню выбора подписки
async def send_subscribe_paid_menu(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    button_name = callback_query.data.replace('button_', '')
    async with BotDataBase() as db:
        keyboard = keyboards.paid_subscription_menu
        text = ''

        if button_name == 'bank_transfer':
            text = 'Оплата банковским переводом\n\n'
            await state.update_data(payment='bank')
        elif button_name == 'cripto_transfer':
            text = 'Оплата переводом на криптокошелёк\n\n'
            await state.update_data(payment='cripto')

        text += 'Выберите тип подписки, которую вы хотите купить/продлить:'

        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=keyboard)
        await state.update_data(subscription_register_menu_id=callback_query.message.message_id)
        await SubscriptionMenu.paid_subscription.set()


# Просим пользователя прислать адрес и пароль для IMAP
async def request_email_password(callback_query: types.CallbackQuery, state: FSMContext):
    button_name = callback_query.data.replace('button_', '')
    current_state = await state.get_state()
    data = await state.get_data()
    subscription_register_menu_id = data.get('subscription_register_menu_id')
    payment = data.get('payment')
    text = ''

    if payment == 'bank':
        text = 'Оплата банковским переводом\n'
    elif payment == 'cripto':
        text = 'Оплата переводом на криптокошелёк\n'

    # узнаём какую подписку хочет получить пользователь
    if button_name == 'base_subscription':
        text += 'Тип подписки: Базовая\n\n'
        await state.update_data(subscription_type='base')
    elif button_name == 'extended_subscription':
        text += 'Тип подписки: Расширенная\n\n'
        await state.update_data(subscription_type='extended')
    elif button_name == 'without_limits_subscription':
        text += 'Тип подписки: Без ограничений\n\n'
        await state.update_data(subscription_type='without_limits')
    elif button_name == 'individual_subscription':
        text += 'Тип подписки: 1 Fansly аккаунт\n\n'
        await state.update_data(subscription_type='individual')
    elif button_name == 'get_free_subscription':
        await SubscriptionMenu.free_subscription_get_user_data.set()

    text += 'Отправьте адрес и пароль для внешних приложений твоей почты mail.ru\n\n' \
            'Как получить пароль для внешних приложений можешь узнать кликнув по кнопке ' \
            '"как настроить бота" из основного меню или по этой ссылке: ' \
            '<a href="https://help.mail.ru/mail/security/protection/external">Как настроить бота</a> \n' \
            'Отправить адрес и пароль нужно одним сообщением через пробел \n\n' \
            'Пример:\nsomeemail@mail.ru yourpassword'

    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=subscription_register_menu_id,
                                text=text,
                                parse_mode='HTML',
                                reply_markup=keyboards.close_menu)


# Получаем отправленный пользователем адрес и пароль и регистрируем пробный аккаунт
async def register_free_bot_account(message: types.Message, state: FSMContext):
    message_data = message.text.split()
    data = await state.get_data()

    # Проверяем отправленный пользователем емаил-адрес и пороль
    if len(message_data) == 2 and is_valid_imap_credentials(message_data[0], message_data[1]):
        async with BotDataBase() as db:
            email_address, password = message_data
            password = await db.encrypt_password(password)
            subscription_expiration_date = await db.get_free_subscription_expiration_date()

            user_id = message.from_user.id
            user_name = message.from_user.full_name

            # Создаём аккаунт пользователя в БД
            await db.add_bot_account(user_id=user_id,
                                     email_login=email_address,
                                     email_password=password,
                                     subscription_type='free',
                                     subscription_status='active',
                                     subscription_expiration_date=subscription_expiration_date)

            # Добавляем пользователя в список авторизованных пользователей
            await db.add_authorized_user(user_id=user_id,
                                         user_name=user_name,
                                         email_login=email_address)

            subscription_register_menu_id = data.get('subscription_register_menu_id')
            await bot.edit_message_text(chat_id=message.chat.id,
                                        message_id=subscription_register_menu_id,
                                        text='Вы успешно зарегистрировались в боте.\n'
                                             'Теперь вам будут приходить уведомления Fansly'
                                             ' c вашей почты\n'
                                             'Для того что бы настроить уведомления перейдите в '
                                             'Основное меню -> Аккаунт',
                                        reply_markup=keyboards.close_menu)

    else:
        await message.answer('Не корректные данные')


# Присылаем меню  подписки
async def request_payment_photo(message: types.Message):
    text = ''


def register_subscription_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_payment_method_menu, lambda c: c.data == 'button_subscribe_menu')
    dp.register_callback_query_handler(skip_button_handler, lambda c: c.data == 'button_skip_free')
    dp.register_callback_query_handler(send_subscribe_paid_menu, lambda c: c.data in ('button_bank_transfer',
                                                                                      'button_cripto_transfer'))
    dp.register_callback_query_handler(request_email_password, lambda c: c.data in ('button_get_free_subscription',
                                                                                    'button_base_subscription',
                                                                                    'button_extended_subscription',
                                                                                    'button_without_limits_subscription',
                                                                                    'button_individual_subscription'),
                                       state='*')
    dp.register_message_handler(register_free_bot_account, state=SubscriptionMenu.free_subscription_get_user_data)
