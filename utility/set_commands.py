from aiogram import Bot
from aiogram.types.bot_command import BotCommand


async def set_commands(bot: Bot) -> None:
    commands = [BotCommand(command="/help", description="Вызвать сообщение с подсказками команд"),
                BotCommand(command="/help_admin", description="Команды администратора"),
                BotCommand(command="/change_id", description="Изменить табельный номер"),
                BotCommand(command="/change_name", description="Изменить ФИО"),
                BotCommand(command="/notifications", description="Запросить уведомления")
                ]
    await bot.set_my_commands(commands)