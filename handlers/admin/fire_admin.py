from aiogram import types
from aiogram.dispatcher import FSMContext

import db
from utility.decorators import check_permission
from keyboards import inline_cancel_keyboard
from classes import FsmAdmin
from utility.cleaner import message_id_dict
from utility import cleaner, search_employee_id


@check_permission
async def fire_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий забрать права администратора у пользователя
    """
    await message.answer(
        'Введите <b>табельный номер</b> или <b>инициалы</b> пользователя, у которого '
        'необходимо забрать права администратора!',
        reply_markup=inline_cancel_keyboard,
        parse_mode=types.ParseMode.HTML)
    await state.set_state(FsmAdmin.fire_admin_state.state)


async def set_fire_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер отзывающий права администратора
    """
    try:
        employee_id = search_employee_id(message)

        if db.get_user_by_employee_id(employee_id).is_admin:
            db.fire_admin(employee_id)
            await message.answer('✔ Права администратора отозваны!',
                                 parse_mode=types.ParseMode.HTML)
        else:
            await message.reply('Пользователь не является администратором!')

        await state.finish()
        await cleaner(message)
    except (KeyError, ValueError) as ex:
        argument = ex.args
        echo = await message.reply(*argument)
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])
