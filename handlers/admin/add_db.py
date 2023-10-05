import os.path as path
from os import remove

from aiogram import types
from asyncio import sleep
from aiogram.dispatcher import FSMContext

import db
from create_bot import bot
from utility.decorators import check_permission
from keyboards import inline_cancel_keyboard
from utility.parser_xlsx import write_from_xlsx_to_db
from classes import FsmAdmin
from utility.cleaner import message_id_dict, cleaner


@check_permission
async def set_file(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для запроса файла exel у пользователя
    """
    await message.reply('Прикрепите exel файл\n(не более 20 Мб!)', reply_markup=inline_cancel_keyboard)
    await state.set_state(FsmAdmin.get_file_state.state)


async def save_file(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий загрузить данные из exel в БД
    Комментарий "*d" к отправляемому фалу позволяет предварительно отчистить БД
    """
    if message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_info = await bot.get_file(message.document.file_id)
        pth = path.join(path.curdir, message.document.file_name)
        await bot.send_chat_action(message.chat.id, types.chat.ChatActions.UPLOAD_DOCUMENT)
        await bot.download_file(file_info.file_path, pth)
        await sleep(1)
        await message.reply('Файл успешно сохранен!\
                            \nЗаписываю данные в БД...')
        match message.caption:
            case str(message.caption) if message.caption.lower() == '*d':
                db.clean_table()
                await message.answer('База данных успешно отчищена!')
        status = write_from_xlsx_to_db(message.document.file_name)
        await message.reply(status)
        await cleaner(message)
        await state.finish()
        if path.isfile(pth):
            remove(pth)
    else:
        await if_not_document(message)


async def if_not_document(message: types.Message):
    echo = await message.reply('Пожалуйста отправьте exel файл!')
    message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])