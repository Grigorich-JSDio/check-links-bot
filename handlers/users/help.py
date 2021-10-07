from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = ("Просто отправь мне текстовый файл в формате `.txt`",
            "Я найду в нём все ссылки, обработаю их и пришлю ответ!")
    
    await message.answer("\n".join(text), parse_mode='Markdown')
