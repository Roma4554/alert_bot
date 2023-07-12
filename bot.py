import logging

from aiogram import executor, Bot
from aiogram.types.bot_command import BotCommand
from aiogram.dispatcher import Dispatcher
from asyncio import create_task
from datetime import date
import os.path as path

from db import sql_start, close_base
from create_bot import dp, bot
from hendlers.user import register_user_handlers
from hendlers.admin import register_admin_handlers
from hendlers.other import register_handlers, create_message_id_list, auto_alert


def logging_enable() -> None:
    """
    Функция включения логирования
    """
    def generate_path_for_log(num: int) -> str:
        today = date.today().isoformat()
        file_name = f'{today}-{num}.log'
        return path.join(path.curdir, 'logs', file_name)

    count = 1
    pth = generate_path_for_log(count)

    while path.exists(pth):
        count += 1
        pth = generate_path_for_log(num=count)

    logging.basicConfig(level=logging.INFO,
                        # filename=pth,
                        filemode='w',
                        encoding='utf-8',
                        format='%(asctime)s [%(module)s] %(levelname)s %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S'
                        )


async def set_commands(bot: Bot) -> None:
    commands = [BotCommand(command="/help", description="Вызвать сообщение с подсказками команд"),
                BotCommand(command="/help_admin", description="Команды администратора"),
                BotCommand(command="/change_id", description="Изменить табельный номер"),
                BotCommand(command="/change_name", description="Изменить ФИО"),
                BotCommand(command="/notifications", description="Запросить уведомления")
                ]
    await bot.set_my_commands(commands)


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

logging_enable()

register_handlers(dp)
register_admin_handlers(dp)
register_user_handlers(dp)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=shutdown)
