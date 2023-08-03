from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.utils import keyboards
from bot.create_bot import bot


class MenuState(StatesGroup):
    pass


async def command_start(message: types.Message):
    text = "Привет! Я бот, созданный для отслеживания уведомлений с сайта Fansly. " \
           "Я могу помочь тебе получать оповещения с твоих аккаунтов Fansly." \
           "Бот может присылать уведомления сразу с большого количества аккаунтов\n" \
           "Вызвать это меню можно по команде /start, /menu\n\n\n" \
           "Выбери одну из следующих опций:\n\n" \
           "|Подписка| - здесь ты можешь купить или продлить свою подписку на меня\n\n" \
           "|Как настроить бота| - здесь вся информация по настройке бота\n\n" \
           "|Аккаунт| - управление твоим аккаунтом бота"
    await bot.send_message(text=text, chat_id=message.chat.id, reply_markup=keyboards.main_menu)


async def send_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    text = "Привет! Я бот, созданный для отслеживания уведомлений с сайта Fansly. " \
           "Я могу помочь тебе получать оповещения с твоих аккаунтов Fansly." \
           "Бот может присылать уведомления сразу с большого количества аккаунтов\n" \
           "Вызвать это меню можно по команде /start, /menu\n\n\n" \
           "Выбери одну из следующих опций:\n\n" \
           "|Подписка| - здесь ты можешь купить или продлить свою подписку на меня\n\n" \
           "|Как настроить бота| - здесь вся информация по настройке бота\n\n" \
           "|Аккаунт| - управление твоим аккаунтом бота"
    await bot.edit_message_text(chat_id=callback_query.message.chat.id,
                                message_id=callback_query.message.message_id,
                                text=text,
                                reply_markup=keyboards.main_menu)

    await state.finish()


def register_main_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'menu'])
    dp.register_callback_query_handler(send_main_menu, lambda c: c.data == 'button_main_menu', state='*')
