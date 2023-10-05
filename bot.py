import logging

from aiogram import executor
from aiogram.dispatcher import Dispatcher
from asyncio import create_task

from db import sql_start, close_base
from create_bot import dp, bot
from handlers.general.register_handlers import register_handlers
from utility import auto_alert, create_message_id_list, logging_enable, set_commands


async def on_startup(_) -> None:
    sql_start()
    create_message_id_list()
    await set_commands(bot)
    logging.info('Бот вышел в сеть')
    create_task(auto_alert(), name='Auto_alert')


async def shutdown(dispatcher: Dispatcher) -> None:
    await dispatcher.storage.close()
    await dp.storage.wait_closed()
    dp.stop_polling()
    close_base()
    logging.info('Бот отключен')


logging_enable(save_to_file=False)
register_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=shutdown)
