import logging

from aiogram import executor, Bot
from aiogram.types.bot_command import BotCommand
from aiogram.dispatcher import Dispatcher

from db import sql_start, close_base
from create_bot import dp, bot
from hendlers.user import register_user_handlers
from hendlers.admin import register_admin_handlers


logging.basicConfig(level=logging.INFO,
                    filename='bot.log',
                    filemode='a',
                    encoding='utf-8',
                    format='%(asctime)s [%(module)s] %(levelname)s %(message)s',
                    datefmt='%d.%m.%Y %H:%M:%S'
                    )


async def set_commands(bot: Bot) -> None:
    commands = [BotCommand(command="/help", description="Вызвать сообщение с подсказками команд"),
                BotCommand(command="/change_id", description="Изменить табельный номер"),
                BotCommand(command="/change_name", description="Изменить ФИО"),
                BotCommand(command="/notifications", description="Запросить уведомления")
                ]
    await bot.set_my_commands(commands)


async def on_startup(_) -> None:
    logging.info('Бот вышел в сеть')
    sql_start()
    await set_commands(bot)


async def shutdown(dispatcher: Dispatcher) -> None:
    await dispatcher.storage.close()
    dp.stop_polling()
    close_base()
    logging.info('Бот отключен')


register_admin_handlers(dp)
register_user_handlers(dp)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup, on_shutdown=shutdown)
