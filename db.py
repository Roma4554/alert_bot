# import sqlite3
from sqlite3 import connect
import logging

from aiogram import types

from classes.User import User
from classes.Notification import Notification


def sql_start() -> None:
    """"
    Функция для подключения к базе данных
    """
    global base, cur
    base = connect('data_base.db')
    cur = base.cursor()
    if base:
        logging.info('База данных успешно подключена')

    base.execute('''CREATE TABLE IF NOT EXISTS user_info(
                    id PRIMARY KEY,
                    name TEXT,
                    employee_id INT,
                    is_admin INT)''')

    base.execute('''CREATE TABLE IF NOT EXISTS table_notification(
                    employee_id INT,
                    date DATE,
                    notification TEXT)''')

    base.commit()


def add_user(message: types.Message) -> None:
    """
    Функция добавляющая id пользователя в таблицу формирования запроса (table_request)
    """
    cur.execute("INSERT INTO user_info(id, name, is_admin) VALUES(:id, :name, :is_admin)",
                dict(id=message.from_user.id, name=message.from_user.full_name, is_admin=0))
    base.commit()


def update_employee_id(value: int, user_id: int) -> None:
    """
    Функция изменяющая табельный номер пользователя
    """
    cur.execute('UPDATE user_info SET employee_id=:value WHERE id=:user_id', dict(value=value, user_id=user_id))
    base.commit()


def update_name(value: str, user_id: int) -> None:
    """
    Функция изменяющая ФИО пользователя
    """
    cur.execute('UPDATE user_info SET name=:value WHERE id=:user_id', dict(value=value, user_id=user_id))
    base.commit()


def add_info_to_notification(value: list[tuple[int, str, str]]) -> None:
    """
    Функция добавляющая значение (value) в таблицу с оповещениями
    """
    cur.executemany('INSERT INTO table_notification VALUES(?, ?, ?)', value)
    base.commit()


def add_admin(user_id: str) -> None:
    """
    Функция добавляющая права администратора пользователю
    """
    cur.execute('UPDATE user_info SET is_admin=1 WHERE id=?', (user_id,))
    base.commit()


def fire_admin(employee_id: str) -> None:
    """
    Функция добавляющая права администратора пользователю
    """
    cur.execute('UPDATE user_info SET is_admin=0 WHERE employee_id=?', (employee_id,))
    base.commit()


def get_user_employee_id(employee_id: int) -> User:
    """
    Функция позволяющая получить экземпляр класса User по табельному номеру
    """
    return User(*cur.execute('SELECT * FROM user_info WHERE employee_id=?', (employee_id,)).fetchone())


def get_user_id(user_id: int) -> User:
    """
    Функция позволяющая получить экземпляр класса User по id
    """
    return User(*cur.execute('SELECT * FROM user_info WHERE id=?', (user_id,)).fetchone())


# def is_admin(user_id: int) -> bool:
#     """
#     Функция позволяющая получить информацию о правах пользователя
#     """
#     return cur.execute('SELECT is_admin FROM user_info WHERE id=?', (user_id,)
#                        ).fetchone()[0] == 1


def get_admin_list() -> User:
    """
    Функция генератор возвращающая список администраторов
    """
    for user in cur.execute('SELECT * FROM user_info WHERE is_admin=1'):
        yield User(*user)


def get_employee_id_dict() -> dict[int, int]:
    """
    Функция возвращающая кортеж (id пользователя, табельный номер)
    """
    return dict(cur.execute('SELECT employee_id, id FROM user_info').fetchall())


def get_notifications_generator() -> Notification:
    """
    Функция генератор возвращающая весь список оповещений
    """
    for result in cur.execute('SELECT * FROM table_notification'):
        yield Notification(*result)


def get_notifications(date: str, employee_id: int) -> list[Notification]:
    """
    Функция возвращающая список оповещений с указанной даты
    """
    result = cur.execute('SELECT * FROM table_notification WHERE date>=? AND employee_id=? ORDER BY date',
                         (date, employee_id)).fetchall()
    if len(result) != 0:
        return [Notification(*note) for note in result]
    else:
        return list()


def clean_table() -> None:
    """
    Функция для отчистки таблицы table_notification
    """
    cur.execute('DELETE FROM table_notification')
    base.commit()


def close_base() -> None:
    """
    Функция закрывающая базу данных
    """
    base.close()
    logging.info('База данных закрыта')
