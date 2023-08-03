from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase
from bot.services.imap_control import is_valid_imap_credentials


class SubscriptionMenu(StatesGroup):
    free_subscription = State()
    free_subscription_get_user_data = State()
    paid_subscription = State()


# Присылаем пользователю меню выбора подписки
async def send_subscribe_menu(callback_query: types.CallbackQuery, state: FSMContext):
    db = BotDataBase()
    user_exist = db.check_user_exist(callback_query.from_user.id)
    keyboard = keyboards.paid_subscription_menu
    text = 'Выберите тип подписки, которую вы хотите купить/продлить:'

    if not user_exist:
        keyboard = keyboards.free_subscription_menu
        text = 'Так как вы не разу ни пользовались ботом, вам доступна бесплатная пробная подписка на 2 дня'
        await SubscriptionMenu.free_subscription.set()
    else:
        await SubscriptionMenu.paid_subscription.set()
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboard)
    await state.update_data(subscription_register_menu_id=callback_query.message.message_id)
    db.close()


# Просим пользователя прислать адрес и пароль для IMAP
async def request_email_password(callback_query: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    subscription_register_menu_id = data.get('subscription_register_menu_id')

    text = 'Отправьте адрес и пароль для внешних приложений твоей почты mail.ru\n\n' \
           'Как получить пароль для внешних приложений можешь узнать кликнув по кнопке ' \
           '"как настроить бота" из основного меню или по этой ссылке: ' \
           '<a href="https://help.mail.ru/mail/security/protection/external">Как настроить бота</a> \n' \
           'Отправить адрес и пароль нужно одним сообщением через пробел \n\n' \
           'Пример:\nsomeemail@mail.ru yourpassword'

    # Бесплатная подписка
    if current_state == SubscriptionMenu.free_subscription.state:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=subscription_register_menu_id,
                                    text=text,
                                    parse_mode='HTML',
                                    reply_markup=keyboards.close_menu)
        await SubscriptionMenu.free_subscription_get_user_data.set()

    # Платная подписка
    elif current_state == SubscriptionMenu.paid_subscription.state:
        await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                    message_id=subscription_register_menu_id,
                                    text=text,
                                    reply_markup=keyboards.close_menu)


# Получаем отправленный пользователем адрес и пароль
async def get_user_email_credentials(message: types.Message, state: FSMContext):
    message_data = message.text.split()
    data = await state.get_data()

    # Проверяем отправленный пользователем емаил-адрес и пороль
    if len(message_data) == 2 and is_valid_imap_credentials(message_data[0], message_data[1]):
        db = BotDataBase()
        email_address, password = message_data
        password = db.encrypt_password(password)
        subscription_expiration_date = db.get_free_subscription_expiration_date()

        user_id = message.from_user.id
        user_name = message.from_user.full_name

        # Создаём аккаунт пользователя в БД
        db.add_bot_account(user_id=user_id,
                           email_login=email_address,
                           email_password=password,
                           subscription_type='free',
                           subscription_status='active',
                           subscription_expiration_date=subscription_expiration_date)

        # Добавляем пользователя в список авторизованных пользователей
        db.add_authorized_user(user_id=user_id,
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
        
        db.close()
    else:
        await message.answer('Не корректные данные')


def register_subscription_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_subscribe_menu, lambda c: c.data == 'button_subscribe_menu')
    dp.register_callback_query_handler(request_email_password, lambda c: c.data == 'button_get_free_subscription',
                                       state='*')
    dp.register_message_handler(get_user_email_credentials, state=SubscriptionMenu.free_subscription_get_user_data)
