import datetime
import logging

from configobj import ConfigObj
from aiogram import types
from asyncio import sleep, current_task
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.utils.exceptions import BotBlocked
from datetime import time, date, timedelta, datetime

import db
from create_bot import bot

config = ConfigObj('settings.ini')

message_id_dict = dict()
notification_dict = dict()


# ==========================Отмена (инлайн кнопка)==================================================
async def cancel_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на нажатие инлайн кнопки "отмена". Прерывает работу машины состояний
    """
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await callback.message.reply('Команда отменена')
    await cleaner(callback)
    await callback.answer()


# ==========================Функция для удаления сообщений из списка============================
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

    try:
        if message_id_dict[user_id]:
            for message_id in message_id_dict[user_id][::-1]:
                await bot.delete_message(chat_id, message_id)

            message_id_dict[user_id].clear()
    except KeyError:
        pass


# ===========================Создание списков для сохранения id сообщений ======================
def create_message_id_list() -> None:
    """
    Функция создающая пустые списки для каждого пользователя в словаре message_id_dict
    """
    for user in db.get_user_list():
        message_id_dict[user.user_id] = []


# ==========================Рассылка оповещения=================================================
async def send_notifications(current_date: datetime.date, user_id: int, employee_id: int) -> bool:
    """
    Асинхронная функция для формирования и отправки сообщения с оповещениями пользователю
    """
    pattern_message = '▫[{data}]: {text}'
    notifications = db.get_notifications(current_date.strftime("%Y.%m.%d"), employee_id)
    if notifications:
        text_message = ('❗<b>Внимание</b>❗').center(39, '=')
        for notification in notifications:
            time_delta = notification.date_to_datetime() - current_date
            if time_delta.days in range(int(config['DEFAULT']['delta_days']) + 1):
                text_message = '\n'.join([text_message, pattern_message.format(data=notification.convert_date(),
                                                                               text=notification.notification)])
        await try_send_message(user_id, text_message)
        return True
    else:
        return False


async def try_send_message(user_id: int, text_message: str) -> None:
    """
    Асинхронная функция для отправки сообщения с оповещениями пользователю
    """
    try:
        await bot.send_message(user_id, text_message, parse_mode=types.ParseMode.HTML)
    except BotBlocked as ex:
        logging.error(f'{ex}. User id: {user_id}')


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


# ==========================Функция для генерации привественного сообщения============================
def start_message_generator(name: str, start: bool = True) -> str:
    helper_user_message = {
        '/help': 'вызвать сообщение с подсказками команд',
        '/change_id': 'изменить табельный номер',
        '/change_name': 'изменить ФИО',
        '/notifications': 'запросить уведомления',
    }

    text_message = f'Привет, {name} 👋!\
                    \nЯ бот который будет напоминать тебе о сдаче необходимых экзаменов!\n\
                    \n⚙ Ты можешь управлять мной с помощью следующих команд:\n'

    for command, description in helper_user_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    if start:
        text_message += '\n\n<b>Для подключения к системе оповещений, пожалуйста, введи свой табельный номер:</b>'

    return text_message


# ==========================Функция для генерации сообщения help_admin============================
def admin_message_generator() -> str:
    helper_admin_message = {
        '/help_admin': 'вызвать сообщение с подсказками',
        '/change_time': 'изменить время рассылки',
        '/change_password': 'изменить пароль',
        '/admin_list': 'получить список администраторов',
        '/fire_admin': 'лишить пользователя прав администратора',
        '/add_note': 'добавить уведомление в базу данных',
        '/add_db': 'добавить уведомления в базу данных из xlsx таблицы (*d в комментарии к файлу предварительно '
                   'отчистит базу данных)',
        '/get_db': 'получить весь список уведомлений из базы данных в виде xlsx таблицы',
    }

    text_message = f'<b>Поздравляю, вам доступны команды администратора! 🔓</b>\n'

    for command, description in helper_admin_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    return text_message


# ==========================Поиск employee_id по инициалам============================
async def search_by_initials(message: types.Message) -> int:
    """
    Асинхронная функция для поиска табельного номера по инициалам пользователя
    """
    if not message.text.isdigit():

        initial_dict = {user.get_initials().lower(): user.employee_id for user in db.get_user_list()}

        text = message.text.strip().replace('. ', '.').lower()
        text = text[:-1:] if text.endswith('.') else text

        for initials in initial_dict:
            if text == initials:
                employee_id = initial_dict[text]
                break
        else:
            echo = await message.reply('Данный пользователь отсутствует в базе!')
            message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])
    else:
        employee_id = message.text

    return employee_id


def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(cancel_call, Text(equals='cancel'), state='*')
