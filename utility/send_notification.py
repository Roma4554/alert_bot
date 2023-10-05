import datetime
import logging

from aiogram import types
from asyncio import sleep, current_task
from aiogram.utils.exceptions import BotBlocked, MessageIsTooLong
from datetime import time, date, timedelta, datetime

import db
from create_bot import bot
from utility.cleaner import config


async def send_notifications(current_date: datetime.date, user_id: int, employee_id: str) -> bool:
    """
    Асинхронная функция для формирования и отправки сообщения с оповещениями пользователю
    """
    pattern_message = '▫[{data}]: {text}'
    notifications = db.get_notifications(current_date.strftime("%Y.%m.%d"), employee_id)
    if notifications:
        text_message = '❗<b>Внимание</b>❗'
        for notification in notifications:
            time_delta = notification.date_to_datetime() - current_date
            if time_delta.days in range(int(config['DEFAULT']['delta_days']) + 1):
                text_message = '\n'.join([text_message, pattern_message.format(data=notification.convert_date(),
                                                                               text=notification.notification)])
        await try_send_message(user_id, text_message)
        return True


async def try_send_message(user_id: int, text_message: str) -> None:
    """
    Асинхронная функция для отправки сообщения с оповещениями пользователю
    """
    try:
        await bot.send_message(user_id, text_message, parse_mode=types.ParseMode.HTML)
    except BotBlocked as ex:
        logging.error(f'{ex}. User id: {user_id}')
    except MessageIsTooLong as ex:
        logging.error(f'{ex}')


async def auto_alert() -> None:
    """
    Функция рассылки сообщений пользователям
    """
    logging.info('Включено оповещение пользователей')
    while True:
        id_dict = db.get_employee_id_dict()
        current_date = date.today()

        current_datetime = datetime.now()
        notification_time = time.fromisoformat(config['DEFAULT']['notification_time'])
        notification_datetime = datetime.combine(current_date, notification_time)

        if notification_datetime > current_datetime:
            notification_datetime += timedelta(days=1)

        delta_time = notification_datetime - current_datetime

        logging.info(f'Следующее оповещение через {int(delta_time.seconds / 60)} мин.')

        await sleep(delta_time.seconds)

        if current_task().cancelled():
            break
        else:
            for employee_id in id_dict:
                user_id = id_dict[employee_id]
                await send_notifications(current_date, user_id, employee_id)

            await sleep(5)

