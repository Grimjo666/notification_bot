from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase
from bot.services.imap_control import is_valid_imap_credentials
from bot.config import subscribe_dict


class SubscriptionMenu(StatesGroup):
    free_subscription = State()
    paid_subscription = State()
    paid_subscription_get_user_data = State()


# присылаем пользователю способ оплаты
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


# обработчик кнопки пропустить
async def skip_button_handler(callback_query: types.CallbackQuery):
    text = 'Выберите способ оплаты:'
    await bot.edit_message_text(message_id=callback_query.message.message_id,
                                chat_id=callback_query.message.chat.id,
                                text=text,
                                reply_markup=keyboards.payment_method_menu)


# Присылаем пользователю меню выбора подписки
async def send_subscribe_paid_menu(callback_query: types.CallbackQuery, state: FSMContext):
    button_name = callback_query.data.split('_')[1]
    async with BotDataBase() as db:
        keyboard = keyboards.paid_subscription_menu
        text = ''

        # Проверяем какая кнопка была нажата и устанавливаем соответствующий текст
        if button_name in subscribe_dict:
            text = f'{subscribe_dict[button_name]}\n\n'
            await state.update_data(payment=button_name)

        text += 'Выберите тип подписки, которую вы хотите купить/продлить:'

        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=callback_query.message.message_id,
                                    text=text,
                                    reply_markup=keyboard)
        await state.update_data(subscription_register_menu_id=callback_query.message.message_id)


# Просим пользователя прислать адрес и пароль для IMAP
async def request_email_password(callback_query: types.CallbackQuery, state: FSMContext):
    button_name = callback_query.data.split('_')
    button_name = f'{button_name[1]}_{button_name[2]}'
    data = await state.get_data()
    subscription_register_menu_id = data.get('subscription_register_menu_id')
    payment = data.get('payment')
    text = ''

    if payment in subscribe_dict:
        text = f'{subscribe_dict[payment]}\n'

    await SubscriptionMenu.paid_subscription.set()

    # узнаём какую подписку хочет получить пользователь
    if button_name in subscribe_dict:
        text += f'Тип подписки: {subscribe_dict[button_name]}\n\n'

        await state.update_data(subscription_type=button_name)

    elif callback_query.data == 'button_get_free_subscription':
        await SubscriptionMenu.free_subscription.set()

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


# Просим пользователя прислать скриншот оплаты
async def request_payment_photo(message: types.Message, state: FSMContext):
    email_login, email_password = message.text.split()
    data = await state.get_data()
    payment = data.get('payment')
    subscription_type = data.get('subscription_type')
    text = ''

    # Проверяем отправленный пользователем емаил-адрес и пароль
    if is_valid_imap_credentials(email_login, email_password):
        await state.update_data(email_login=email_login, email_password=email_password)

        if payment in subscribe_dict:
            text = f'{subscribe_dict[payment]}\n'

        if subscription_type in subscribe_dict:
            text += f'Тип подписки: {subscribe_dict[subscription_type]}\n\n'

        text += 'Теперь оплатите подписку и пришлите скриншот оплаты\n\nРеквизиты: 0000-000-000-000'
        await bot.send_message(chat_id=message.chat.id, text=text)
        await SubscriptionMenu.paid_subscription_get_user_data.set()
    else:
        await message.answer('Не корректные данные')


# Хэндлер для получения скриншота оплаты и записи запроса на доступ к аккаунту в БД
async def response_payment_photo(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email_login = data.get('email_login')
    email_password = data.get('email_password')
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    subscription_type = data.get('subscription_type')
    payment_type = data.get('payment')

    # Получаем фотографию из сообщения
    if message.photo:
        payment_photo = message.photo[-1].file_id  # Берем самую большую версию фото из сообщения
        async with BotDataBase() as db:
            email_password = await db.encrypt_password(email_password)  # шифруем пароль
            # Добавляем запрос на регистрацию аккаунта в БД
            await db.add_buy_request(user_id, user_name, email_login, email_password,
                                     subscription_type, payment_photo, payment_type)
            await message.answer("Спасибо! Ваша оплата для доступа к аккаунту принята."
                                 " Мы свяжемся с вами после проверки оплаты.")
            await state.finish()
    else:
        # Обработка случая, если фотография не была предоставлена
        await message.answer("Пожалуйста, отправьте скриншот оплаты в виде фотографии.")


def register_subscription_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_payment_method_menu, lambda c: c.data == 'button_subscribe_menu')
    dp.register_callback_query_handler(skip_button_handler, lambda c: c.data == 'button_skip_free')
    dp.register_callback_query_handler(send_subscribe_paid_menu, lambda c: c.data in ('button_bank_transfer',
                                                                                      'button_cripto_transfer'))
    dp.register_callback_query_handler(request_email_password, lambda c: c.data in (
                                                                        'button_get_free_subscription',
                                                                        'button_base_subscription',
                                                                        'button_extended_subscription',
                                                                        'button_without_limits_subscription',
                                                                        'button_individual_subscription'), state='*')
    dp.register_message_handler(register_free_bot_account, state=SubscriptionMenu.free_subscription)
    dp.register_message_handler(request_payment_photo, state=SubscriptionMenu.paid_subscription)
    dp.register_message_handler(response_payment_photo, state=SubscriptionMenu.paid_subscription_get_user_data,
                                content_types=['photo', 'text'])