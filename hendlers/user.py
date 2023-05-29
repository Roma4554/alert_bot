import logging
from datetime import date

from aiogram import types
from sqlite3 import IntegrityError
from aiogram.dispatcher import FSMContext, Dispatcher

import db
from create_bot import bot
from keyboards import inline_cancel_keyboard
from classes import FSM_user
from hendlers.box import config, message_id_dict
from hendlers.box import start_message_generator, admin_message_generator
from hendlers.box import cleaner, send_notifications


# ==========================Старт==================================================
async def start(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на команду /start
    """
    try:
        db.add_user(message)
        logging.info(f'Пользователь {message.from_user.full_name} успешно добавлен в базу данных')
        message_id_dict[message.from_user.id] = list()
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

    if message.text.isdigit() and len(message.text) == int(config['DEFAULT']['len_employee_id']):
        db.update_employee_id(message.text, message.from_user.id)
        await message.reply(f'Табельный номер {message.text} сохранен!')
        message_id_dict[message.from_user.id].append(message.message_id)
        await cleaner(message)
        await state.finish()

    else:
        echo = await message.reply('Табельный номер введен неверно.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])


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
