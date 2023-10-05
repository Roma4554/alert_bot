from re import search

from aiogram import types
from aiogram.dispatcher import FSMContext


from keyboards import inline_cancel_keyboard
from utility.decorators import check_permission
from classes import FsmAdmin
from utility.cleaner import config, message_id_dict, cleaner


password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[\s#`~"\'\.\+\-\\\/\*$%№@;:^&\*\=]).*$'


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
        await message.answer('✔ Пароль успешно изменен!',
                             parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].append(message.message_id)
        await state.finish()
        await cleaner(message)
    else:
        echo = await message.reply('Некорректный пароль.\
                                    \nПароль должен содержать строчные и прописные латинские буквы, цифры!')
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])
