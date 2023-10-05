from aiogram import types

import db
from utility.decorators import check_permission


@check_permission
async def get_admin_list(message: types.Message) -> None:
    """
    Хендлер предоставляющий список пользователей имеющих статус администратора
    """
    pattern = '{num}) {user}; Табельный номер: {employee_id}.'
    text_message = "📜 <b>Список администраторов:</b>"
    for num, admin in enumerate(db.get_user_list(only_admin=True), start=1):
        text_message = '\n'.join([text_message, pattern.format(num=num,
                                                               user=admin.name,
                                                               employee_id=admin.employee_id)])
    await message.reply(text_message,
                        parse_mode=types.ParseMode.HTML)
