from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re

from bot.utils import keyboards
from bot.create_bot import bot
from bot.services import db_control


class AdminMenuState(StatesGroup):
    edit_model_name = State()
    del_model_name = State()
    add_notification = State()
    del_notification = State()
    add_user = State()
    del_user = State()


async def edit_model_name_handler(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Введи почту и ник модели.\n'
                                     'Пример: somemail@mail.ru Eva\n',
                                reply_markup=keyboards.del_model_name_menu)

    await state.update_data(message_id=callback_query.message.message_id,
                            count_add_model=0)
    await AdminMenuState.edit_model_name.set()


async def send_del_model_name_keyboard(callback_query: types.CallbackQuery):
    await callback_query.message.answer('Выбери модель для удаления:',
                                        reply_markup=keyboards.create_models_keyboard())
    await AdminMenuState.del_model_name.set()


async def del_model_name_handler(message: types.Message):
    model = message.text.split()[0]
    db_control.del_model(model)


# Запись в таблицу models
async def write_model_to_db(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('message_id')
    counter = 1
    counter += data.get('count_add_model')  # Получаем счётчик добавленных моделей

    model_data = message.text.split()
    model_email = model_data[0]
    model_name = ' '.join(model_data[1:])

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if re.match(pattern, model_email):

        db_control.add_model(model_email, model_name)
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Введи почту и ник модели.\n'
                                         'Пример: somemail@mail.ru Eva\n\n\n'
                                         f'Модель добавлена или изменена ({counter})',
                                    reply_markup=keyboards.close_menu)
        await state.update_data(count_add_model=counter)  # Обновляем счётчик добавленных моделей
    else:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Введи почту и ник модели.\n'
                                         'Пример: somemail@mail.ru Eva\n\n\n'
                                         'Не корректные данные',
                                    reply_markup=keyboards.close_menu)


async def add_user_menu(callback_query: types.CallbackQuery):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Отправь ID пользователя и его имя\n'
                                     'Пример "77777777 Eva Elfi"',
                                reply_markup=keyboards.close_menu)

    await AdminMenuState.add_user.set()


async def add_user_access(message: types.Message):
    user_id, *name = message.text.split()
    if name is None:
        name = '-----'
    name = ' '.join(name)
    if user_id.isdigit():
        db_control.add_user(user_id, name)
        await message.answer(f'Доступ для {name} разрешён')
    else:
        await message.answer('Не корректный ID')


async def del_user_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text='Отправь ID пользователя или выбери его на клавиатуре',
                                reply_markup=keyboards.del_user_menu)

    await AdminMenuState.del_user.set()
    await state.update_data(del_menu_id=callback_query.message.message_id)


async def del_user_access(message: types.Message, state: FSMContext):
    data = await state.get_data()
    message_id = data.get('del_menu_id')

    user_data = message.text.split()
    user_id = user_data[0]
    user_name = ' '.join(user_data[1:]).replace('/', '')

    if db_control.check_user_access(user_id):
        print(user_id)
        db_control.del_user(user_id)
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message_id,
                                    text='Отправь ID пользователя или выбери его на клавиатуре\n\n'
                                         f'Пользователь: {user_name} удалён',
                                    reply_markup=keyboards.del_user_menu)

    else:
        await message.answer('Не верный ID')


# Отправляем клаву с ID и никами пользователей
async def send_users_buttons(callback_query: types.CallbackQuery):
    users_buttons = keyboards.create_users_keyboard()
    if users_buttons:
        await callback_query.message.answer(reply_markup=users_buttons, text='Пользователи:')
    else:
        await callback_query.message.answer('Нет пользователей с доступом')


# Отправляем клаву с никами моделей
async def send_models_buttons(callback_query: types.CallbackQuery):
    models_buttons = keyboards.create_models_keyboard()
    await callback_query.message.answer(reply_markup=models_buttons, text='Модели:')


def register_main_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(edit_model_name_handler, lambda c: c.data == 'button_edit_model_name_menu')
    dp.register_message_handler(write_model_to_db, state=AdminMenuState.edit_model_name)
    dp.register_callback_query_handler(send_models_buttons, lambda c: c.data == 'button_show_models', state='*')
    dp.register_callback_query_handler(send_users_buttons, lambda c: c.data == 'button_show_users', state='*')
    dp.register_callback_query_handler(add_user_menu, lambda c: c.data == 'button_add_user_menu')
    dp.register_message_handler(add_user_access, state=AdminMenuState.add_user)
    dp.register_callback_query_handler(del_user_menu, lambda c: c.data == 'button_del_user_menu')
    dp.register_message_handler(del_user_access, state=AdminMenuState.del_user)
    dp.register_callback_query_handler(send_del_model_name_keyboard,
                                       lambda c: c.data == 'button_del_model_name_keyboard',
                                       state='*')
    dp.register_message_handler(del_model_name_handler, state=AdminMenuState.del_model_name)
