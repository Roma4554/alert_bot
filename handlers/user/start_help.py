import logging

from aiogram import types
from sqlite3 import IntegrityError
from aiogram.dispatcher import FSMContext

import db
from classes import FsmUser
from utility import start_message_generator
from utility.cleaner import message_id_dict

async def start(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на команду /start
    """
    try:
        db.add_user(message)
        logging.info(f'Пользователь {message.from_user.full_name} успешно добавлен в базу данных')
        message_id_dict[message.from_user.id] = list()
        await message.answer(start_message_generator(message.from_user.first_name),
                             parse_mode=types.ParseMode.HTML)
    except IntegrityError:
        user = db.get_user_by_id(message.from_user.id)
        if user.employee_id != '0':
            if len(user.name.split()) == 3:
                await message.answer('Вы уже зарегистрированы!')
                logging.debug(f'Пользователь {message.from_user.full_name} уже есть в базе данных')
            else:
                await message.answer('В базе отсутствует Ваше ФИО.'
                                     '\nПожалуйста, введите ФИО через пробел:')
                await state.set_state(FsmUser.get_full_name_state.state)
            return
        else:
            await message.answer(start_message_generator(message.from_user.first_name),
                                 parse_mode=types.ParseMode.HTML)

    await state.set_state(FsmUser.get_employee_id_from_start_state.state)


async def help_user(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /help
    """
    await message.answer(start_message_generator(message.from_user.first_name, start=False),
                         parse_mode=types.ParseMode.HTML)
