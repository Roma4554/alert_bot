import logging
import datetime
from datetime import date

from aiogram import types
from sqlite3 import IntegrityError
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.utils.exceptions import BotBlocked


import db
from create_bot import bot
from keyboards import inline_cancel_keyboard
from classes import FSM_user
from box import config, message_id_dict, cleaner
from box import start_message_generator, admin_message_generator


# ==========================Старт==================================================
async def start(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на команду /start
    """
    try:
        db.add_user(message)
        logging.info(f'Пользователь {message.from_user.full_name} успешно добавлен в базу данных')
    except IntegrityError:
        logging.error(f'Пользователь {message.from_user.full_name} уже есть в базе данных')

    await message.answer(start_message_generator(message.from_user.first_name),
                         reply_markup=inline_cancel_keyboard,
                         parse_mode=types.ParseMode.HTML)

    await state.set_state(FSM_user.get_employee_id_state.state)


# ==========================Хелп==================================================
async def help_user(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /help
    """
    await message.answer(start_message_generator(message.from_user.first_name, start=False),
                         parse_mode=types.ParseMode.HTML)


# ==========================Изменение табельного номера==================================================
async def get_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для замены табельного номера
    """
    await message.answer('Введите табельный номер:', reply_markup=inline_cancel_keyboard)

    await state.set_state(FSM_user.get_employee_id_state.state)


async def set_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий табельный номер пользователя
    """
    if message.from_user.id not in message_id_dict.keys():
        message_id_dict[message.from_user.id] = list()

    message_id_dict[message.from_user.id].append(message.message_id)

    if message.text.isdigit() and len(message.text) == int(config['DEFAULT']['len_employee_id']):
        db.update_employee_id(message.text, message.from_user.id)
        await message.reply(f'Табельный номер {message.text} сохранен!')
        await cleaner(message)
        await state.finish()

    else:
        echo = await message.reply('Табельный номер введен неверно.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].append(echo.message_id)


# ==========================Изменение ФИО==================================================
async def get_full_name(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для замены ФИО
    """
    await message.answer('Введите ФИО через пробел:', reply_markup=inline_cancel_keyboard)
    await state.set_state(FSM_user.get_full_name_state.state)


async def set_full_name(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий табельный номер пользователя
    """
    if message.from_user.id not in message_id_dict.keys():
        message_id_dict[message.from_user.id] = list()

    message_id_dict[message.from_user.id].append(message.message_id)

    full_name = message.text.split()
    if all(map(str.isalpha, full_name)) and len(full_name) == 3:
        db.update_name(message.text, message.from_user.id)
        await message.reply(f'ФИО: {message.text} сохранено!')
        await cleaner(message)
        await state.finish()
    else:
        echo = await message.reply('Некорректный формат ФИО.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].append(echo.message_id)


# ==========================Получение статуса администратора==================================================
async def get_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий получить статус администратора
    """
    await message.answer('Для получения статуса администратора, пожалуйста, введите пароль:',
                         reply_markup=inline_cancel_keyboard)
    await state.set_state(FSM_user.get_admin_state.state)


async def set_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий статус администратора при правильном вводе пароля
    """
    if message.from_user.id not in message_id_dict.keys():
        message_id_dict[message.from_user.id] = list()

    if message.text == config['topsecret']['admin_password']:
        db.add_admin(message.from_user.id)
        await message.answer(admin_message_generator(),
                             parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].append(message.message_id)
        await cleaner(message)
        await state.finish()
    else:
        echo = await message.answer('Пароль введен неверно.\nПопробуйте еще раз!')
        await bot.delete_message(message.chat.id, message.message_id)
        message_id_dict[message.from_user.id].append(echo.message_id)


# ==========================Запрос оповещения==================================================
async def notification(message: types.Message) -> None:
    """
    Хендлер для получения уведомлений из БД
    """
    current_date = date.today()
    user_id = message.from_user.id
    await send_notifications(current_date, user_id)


async def send_notifications(current_date: datetime.date, user_id: int) -> None:
    pattern_message = '[{data}]: {text}'
    text_message = '!Внимание!'.center(35, '=')
    notifications = db.get_notifications(current_date.strftime("%Y.%m.%d"), db.get_user_id(user_id).employee_id)
    if len(notifications) == 0:
        text_message = 'Нет уведомлений...'
    else:
        for notification in notifications:
            time_delta = notification.date_to_datetime() - current_date
            if time_delta.days in range(int(config['DEFAULT']['delta_days']) + 1):
                text_message = '\n'.join([text_message, pattern_message.format(data=notification.convert_date(),
                                                                               text=notification.notification)])
    try:
        await bot.send_message(user_id, text_message)
    except BotBlocked as ex:
        logging.error(f'{ex}: Пользователь заблокировал бота')


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_user, commands=['help'])
    dp.register_message_handler(get_employee_id, commands=['change_id'])
    dp.register_message_handler(set_employee_id, state=FSM_user.get_employee_id_state)
    dp.register_message_handler(get_full_name, commands=['change_name'])
    dp.register_message_handler(set_full_name, state=FSM_user.get_full_name_state)
    dp.register_message_handler(get_admin, commands=['get_admin'])
    dp.register_message_handler(set_admin, state=FSM_user.get_admin_state)
    dp.register_message_handler(notification, commands=['notifications'])

