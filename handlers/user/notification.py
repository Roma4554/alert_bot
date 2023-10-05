from datetime import date
from aiogram import types

import db
from utility import send_notifications


async def notification(message: types.Message) -> None:
    """
    Хендлер для получения уведомлений из БД
    """
    current_date = date.today()
    user_id = message.from_user.id
    employee_id = db.get_user_by_id(user_id).employee_id
    state = await send_notifications(current_date, user_id, employee_id)
    if not state:
        await message.answer('Упс...\nКажется пусто 🥺.')