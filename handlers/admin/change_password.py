from re import search
from logging import info

from aiogram import types
from aiogram.dispatcher import FSMContext

import db
from keyboards import inline_cancel_keyboard
from utility.decorators import check_permission
from classes import FsmAdmin
from utility.cleaner import config, message_id_dict, cleaner
from utility.patterns_for_re import password_pattern


@check_permission
async def change_password(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий изменить пароль администратора
    """
    await message.answer('🔑 <b>Введите новый пароль!</b>\
                         \nПароль должен содержать строчные и прописные латинские буквы, цифры',
                         reply_markup=inline_cancel_keyboard,
                         parse_mode=types.ParseMode.HTML)

    await state.set_state(FsmAdmin.change_password_state.state)


async def set_new_password(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий новый пароль для получения прав администратора
    """

    if search(password_pattern, message.text):
        config['topsecret']['admin_password'] = message.text
        config.write()
        info(f"Пользователь {db.get_user_by_id(message.from_user.id).get_initials()} изменил пароль")
        await message.answer('✔ Пароль успешно изменен!',
                             parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].append(message.message_id)
        await state.finish()
        await cleaner(message)
    else:
        echo = await message.reply('Некорректный пароль.\
                                    \nПароль должен содержать строчные и прописные латинские буквы, цифры!')
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])
