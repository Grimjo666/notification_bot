from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import re

from bot.utils import keyboards
from bot.create_bot import bot
from bot.models.bot_database_control import BotDataBase


async def command_pay_requests(message: types.Message):
    async with BotDataBase() as db:
        result = await db.get_buy_requests()
        await bot.send_photo(chat_id=message.chat.id, photo=result[-1][-2])
        await message.answer(result)


def register_admin_menu_handlers(dp: Dispatcher):
    dp.register_message_handler(command_pay_requests, commands='pay')


