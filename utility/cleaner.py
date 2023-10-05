from configobj import ConfigObj
from aiogram import types

import db
from create_bot import bot


config = ConfigObj('settings.ini')

message_id_dict = dict()
notification_dict = dict()

def create_message_id_list() -> None:
    """
    Функция создающая пустые списки для каждого пользователя в словаре message_id_dict
    """
    for user in db.get_user_list():
        message_id_dict[user.user_id] = []


async def cleaner(call: types.Message | types.CallbackQuery) -> None:
    """
    Асинхронная функция удаляющая сообщения в сохраненном списке словаря message_id_dict и отчищающая список
    """
    user_id = call.from_user.id

    if isinstance(call, types.Message):
        chat_id = call.chat.id
    elif isinstance(call, types.CallbackQuery):
        chat_id = call.message.chat.id
    else:
        raise TypeError('call должен быть Message или CallbackQuery')

    while message_id_dict[user_id]:
        await bot.delete_message(chat_id, message_id_dict[user_id].pop())