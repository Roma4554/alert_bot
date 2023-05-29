import functools
from typing import Callable
import logging
import time

from aiogram import types

import db
from create_bot import bot


def check_permission(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapped(message: types.Message, *args, **kwargs):
        try:
            if db.get_user_id(message.from_user.id).is_admin:
                return await func(message, *args, **kwargs)
            else:
                raise PermissionError(
                    f'У пользователя {message.from_user.full_name} недостаточно прав для выполнения функции {func.__name__}')
        except PermissionError as exp:
            await bot.send_message(message.from_user.id, 'У Вас недостаточно прав для выполнения команды!')
            logging.error('{exp_name}: {exp_str}'.format(exp_name='PermissionError',
                                                         exp_str=exp))

    return wrapped


def log(func: Callable) -> Callable:
    @functools.wraps(func)
    async def wrapper(message: types.Message, *args, **kwargs):
        logging.info('- Запускается функция {name}'.format(name=func.__qualname__))
        started_at = time.time()
        result = await func(message, *args, **kwargs)
        ended_at = time.time()
        elapsed = round(ended_at - started_at, 3)
        logging.info('- Завершение функции {name}, время работы = {elapsed}s'.format(name=func.__qualname__,
                                                                                     elapsed=elapsed))
        return result

    return wrapper
