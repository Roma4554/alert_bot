import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

import db
from keyboards import inline_cancel_keyboard
from create_bot import bot
from classes import FsmUser
from utility.cleaner import message_id_dict, cleaner, config
from utility import admin_message_generator

async def get_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий получить статус администратора
    """
    await message.answer('🔐 Для получения статуса администратора, пожалуйста, введите пароль:',
                         reply_markup=inline_cancel_keyboard)
    await state.set_state(FsmUser.get_admin_state.state)


async def set_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий статус администратора при правильном вводе пароля
    """
    if message.text == config['topsecret']['admin_password']:
        db.add_admin(message.from_user.id)
        await message.answer(admin_message_generator(),
                             parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].append(message.message_id)
        logging.info(f'Пользователь {db.get_user_by_id(message.from_user.id).name} становится администратором')
        await cleaner(message)
        await state.finish()
    else:
        echo = await message.answer('🔒 Пароль введен неверно.\nПопробуйте еще раз!')
        await bot.delete_message(message.chat.id, message.message_id)
        message_id_dict[message.from_user.id].append(echo.message_id)