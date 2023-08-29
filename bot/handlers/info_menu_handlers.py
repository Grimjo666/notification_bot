from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.exceptions import ChatNotFound
from aiogram.types import InputFile
from sqlite3 import IntegrityError
import logging

from bot.models.bot_database_control import BotDataBase, DBErrors
from bot.utils import keyboards
from bot.create_bot import bot


async def send_info_menu(callback_query: types.CallbackQuery):
    text = 'Для начала вам нужно настроить пересылку сообщений на почту Mail.ru'
    await bot.send_message(chat_id=callback_query.from_user.id,
                           text=text)