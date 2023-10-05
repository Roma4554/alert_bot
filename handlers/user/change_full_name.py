from aiogram import types
from aiogram.dispatcher import FSMContext

import db
from keyboards import inline_cancel_keyboard
from classes import FsmUser
from utility.cleaner import message_id_dict, cleaner




async def get_full_name(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для замены ФИО
    """
    await message.answer('🖊 Введите ФИО через пробел:', reply_markup=inline_cancel_keyboard)
    await state.set_state(FsmUser.get_full_name_state.state)


async def set_full_name(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий табельный номер пользователя
    """
    message_id_dict[message.from_user.id].append(message.message_id)
    full_name = message.text.split()
    if all(map(str.isalpha, full_name)) and len(full_name) == 3:
        full_name = ' '.join(map(str.capitalize, full_name))
        db.update_name(full_name, message.from_user.id)
        await message.reply(f'✔ <b>ФИО:</b> <u>{full_name}</u> сохранено!',
                            parse_mode=types.ParseMode.HTML)
        await cleaner(message)
        await state.finish()
    else:
        echo = await message.reply('✖ Некорректный формат ФИО.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].append(echo.message_id)