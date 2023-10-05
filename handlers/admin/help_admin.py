from aiogram import types

from utility.decorators import check_permission
from utility import admin_message_generator


@check_permission
async def help_admin(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /help_admin
    """
    await message.answer(admin_message_generator(),
                         parse_mode=types.ParseMode.HTML)
