import os.path as path
from os import remove

from aiogram import types
from asyncio import sleep
from aiogram.types import InputFile


from create_bot import bot
from utility.decorators import check_permission
from utility.parser_xlsx import write_from_db_to_xlsx


@check_permission
async def get_file(message: types.Message) -> None:
    """
    Хендлер формирующий exel файл с данными из БД и отправляющий его пользователю
    """
    await message.reply('Формируем xlsx файл...')
    write_from_db_to_xlsx()
    pth = path.join(path.curdir, 'DataBase.xlsx')
    fail = InputFile(pth)
    await bot.send_chat_action(message.chat.id, types.chat.ChatActions.UPLOAD_DOCUMENT)
    await sleep(1)
    await bot.send_document(chat_id=message.chat.id, document=fail)
    if path.isfile(pth):
        remove(pth)
