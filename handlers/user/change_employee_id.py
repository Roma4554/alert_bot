import asyncio

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import Message

import db
from keyboards import inline_cancel_keyboard
from classes import FsmUser
from utility.cleaner import message_id_dict, cleaner, config


async def get_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для замены табельного номера
    """
    await message.answer('🖊 Введите табельный номер:', reply_markup=inline_cancel_keyboard)
    await state.set_state(FsmUser.get_employee_id_state.state)


async def set_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий табельный номер пользователя
    """
    employee_id = set(db.get_employee_id_dict().keys())

    if message.text.isdigit() and len(message.text) == int(config['DEFAULT']['len_employee_id']):

        if employee_id.intersection({message.text}):
            echo = await message.reply('❗Данный табельный номер уже зарегистрирован❗\nПопробуйте еще раз.')
            message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])
            return

        db.update_employee_id(message.text, message.from_user.id)
        await message.reply(f'✔ <b>Табельный номер:</b> <u>{message.text}</u> сохранен!',
                            parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].append(message.message_id)
        await cleaner(message)

        current_state = await state.get_state()
        if current_state == 'FsmUser:get_employee_id_from_start_state':
            await asyncio.sleep(0.5)
            echo: Message = await message.answer(f'🖊 Введите ФИО через пробел:')
            message_id_dict[message.from_user.id].append(echo.message_id)
            await state.set_state(FsmUser.get_full_name_state.state)
        else:
            await state.finish()

    else:
        echo = await message.reply('✖ Табельный номер введен неверно.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])
