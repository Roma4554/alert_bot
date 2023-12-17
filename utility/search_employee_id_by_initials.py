from aiogram import types
from re import search

import db
from utility.cleaner import config
from patterns_for_re import initial_pattern


def search_employee_id(message: types.Message) -> str:
    """
    Функция для поиска табельного номера по инициалам пользователя
    """
    if not message.text.isdigit():
        if not search(initial_pattern, message.text):
            raise ValueError('Введите данные в формате Фамилия И.О.')

        initial_dict = {user.get_initials().lower(): user.employee_id for user in db.get_user_list()}

        text = message.text.strip().replace('. ', '.').lower()
        text = text[:-1:] if text.endswith('.') else text

        for initials in initial_dict:
            if text == initials:
                employee_id = initial_dict[text]
                break
        else:
            raise KeyError('Данный пользователь отсутствует в базе данных!')

    elif len(message.text) != int(config['DEFAULT']['len_employee_id']):
        raise ValueError(f"Табельный номер: {config['DEFAULT']['len_employee_id']}-значное целочисленное значение")

    else:
        text_message = message.text
        user_list = (user.employee_id for user in db.get_user_list())
        if text_message in user_list:
            employee_id = text_message
        else:
            raise KeyError('Данный пользователь отсутствует в базе данных!')

    return employee_id

