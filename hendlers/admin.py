import logging
import os.path as path
from os import remove
from datetime import time, date, timedelta, datetime
from re import search

from aiogram import types
from asyncio import sleep
from aiogram.types import InputFile
from aiogram.dispatcher import FSMContext
from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from sqlite3 import OperationalError

import db
from create_bot import bot
from decorators import check_permission, log
from keyboards import inline_cancel_keyboard, inline_save_notification_keyboard
from parser_xlsx import write_from_xlsx_to_db, write_from_db_to_xlsx
from classes import Notification, FSM_admin
from box import config, message_id_dict, notification_dict, cleaner
from box import admin_message_generator
from hendlers.user import send_notifications


# ==========================Хелп_админ==================================================
@check_permission
async def help_admin(message: types.Message) -> None:
    """
    Хенделер срабатывающий на команду /help_admin
    """
    await message.answer(admin_message_generator(),
                         parse_mode=types.ParseMode.HTML)


# ==========================Рассылка оповещений==================================================
@check_permission
async def alert(message: types.Message) -> None:
    """
    Функция рассылки сообщений пользователям
    """

    logging.info('Включено оповещение пользователей')
    await message.reply('Оповещение пользователей включено!')

    while True:
        id_dict = db.get_employee_id_dict()
        current_date = date.today()

        for employee_id in id_dict:
            user_id = id_dict[employee_id]
            await send_notifications(current_date, user_id)

        current_datetime = datetime.now()
        notification_time = time.fromisoformat(config['DEFAULT']['notification_time'])
        notification_datetime = datetime.combine(current_date, notification_time)

        if notification_datetime > current_datetime:
            notification_datetime += timedelta(days=1)

        delta_time = notification_datetime - current_datetime

        logging.info(f'Следующее оповещение через {int(delta_time.seconds / 60)} мин.')

        await sleep(delta_time.seconds)


# ==========================Изменение времени рассылки оповещений==================================================
@check_permission
async def change_notification_time(message: types.Message, state: FSMContext) -> None:
    await message.answer('Введите новое время оповещения в формате ЧЧ:ММ:CC или ЧЧ:ММ.',
                         reply_markup=inline_cancel_keyboard)
    await state.set_state(FSM_admin.get_new_notification_time.state)


async def set_notification_time(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер изменяющий время оповещения пользователя
    """
    pattern = r'([01]\d|2[0-4]):[0-5]\d(:[0-5]\d)?$'
    if search(pattern, message.text):
        if len(message.text.split(':')) == 2:
            new_time = ':'.join([message.text, '00'])
        else:
            new_time = message.text
        config['DEFAULT']['notification_time'] = new_time
        config.write()
        await message.reply('Время оповещения успешно изменено на {time}!'
                            .format(time=new_time))
        await state.finish()
    else:
        await message.reply('Некорректный формат времени.\nПопробуйте еще раз!')


# ==========================Забрать права администратора==================================================
@check_permission
async def fire_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий забрать права администратора у пользователя
    """
    await message.answer('Введите табельный номер пользователя, у которого необходимо забрать права администратора!',
                         reply_markup=inline_cancel_keyboard)
    await state.set_state(FSM_admin.fire_admin_state.state)


async def set_fire_admin(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер отзывающий права администратора
    """
    try:
        if db.get_user_employee_id(message.text).is_admin:
            db.fire_admin(message.text)
            await message.answer('Права администратора отозваны!')
        else:
            await message.reply('Пользователь не является администратором!')

    except (TypeError, OperationalError):
        await message.reply('Пользователь с таким табельным номером отсутствует!')

    finally:
        await state.finish()


# ==========================Изменение пароля=========================================================
@check_permission
async def change_password(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий изменить пароль администратора
    """
    await message.answer('Введите новый пароль!\
                         \nПароль должен содержать строчные и прописные латинские буквы, цифры',
                         reply_markup=inline_cancel_keyboard)

    await state.set_state(FSM_admin.change_password_state.state)


async def set_new_password(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий новый пароль для получения прав администратора
    """
    pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[\s#`~"\'\.\+\-\\\/\*$%№@;:^&\*\=]).*$'
    if message.from_user.id not in message_id_dict:
        message_id_dict[message.from_user.id] = list()

    if search(pattern, message.text):
        config['topsecret']['admin_password'] = message.text
        config.write()
        echo = await message.answer('Пароль успешно изменен!')
        await state.finish()
        await cleaner(message)
    else:
        echo = await message.reply('Некорректный пароль.\
                                    \nПароль должен содержать строчные и прописные латинские буквы, цифры!')

    message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])

# ==========================Список администраторов==================================================
@check_permission
async def get_admin_list(message: types.Message) -> None:
    """
    Хендлер предоставляющий список пользователей имеющих статус администратора
    """
    pattern = '{num}) {user}; Табельный номер: {employee_id}.'
    text_message = "Список администраторов:"
    for num, admin in enumerate(db.get_admin_list(), start=1):
        text_message = '\n'.join([text_message, pattern.format(num=num,
                                                               user=admin.name,
                                                               employee_id=admin.employee_id)])
    await message.reply(text_message)


# ==========================Загрузка данных в БД из telegram==================================================
@check_permission
async def add_notification(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для добавления оповещения пользователя
    """
    echo = await message.reply('Введите табельный номер пользователя:', reply_markup=inline_cancel_keyboard)
    message_id_dict[message.from_user.id] = [echo.message_id]

    await state.set_state(FSM_admin.add_employee_id_state.state)


async def add_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер сохраняющий табельный номер и запрашивающий дату оповещения:
    """
    notification_dict[message.from_user.id] = Notification()
    try:
        notification_dict[message.from_user.id].employee_id = int(message.text)
    except (TypeError, ValueError):
        echo = await message.reply(
            f"Табельный номер: {config['DEFAULT']['len_employee_id']}-значное целочисленное значение")
    else:
        echo = await message.reply('Введите дату в формате ДД.ММ.ГГГГ:', reply_markup=inline_cancel_keyboard)
        await state.set_state(FSM_admin.add_date_state.state)
    finally:
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])


async def add_date(message: types.Message, state: FSMContext) -> None:
    pattern = r'^(?:0[1-9]|[12]\d|3[01])\.(?:0[1-9]|1[012])\.(?:[12]\d{3})$'

    if search(pattern, message.text):
        split_text = message.text.split('.')[::-1]
        date = '.'.join(split_text)
        notification_dict[message.from_user.id].date = date
        await state.set_state(FSM_admin.add_note_state.state)
        echo = await message.reply('Введите текст уведомления:',  reply_markup=inline_cancel_keyboard)
    else:
        echo = await message.reply('Некорректный формат даты! Попробуйте еще раз:')

    message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])


async def add_text(message: types.Message) -> None:
    notification = notification_dict[message.from_user.id]
    notification.notification = message.text
    text_message = 'Чтобы изменить текст, повторно отправьте сообщение!' \
                   'Для сохранения конечной версии, нажмите кнопку "Сохранить"\n' \
                   '\nПредварительный просмотр:'
    text_message = '\n'.join([text_message, str(notification)])
    echo = await message.answer(text_message, reply_markup=inline_save_notification_keyboard)
    message_id_dict[message.from_user.id].append(message.message_id)
    await cleaner()

    message_id_dict[message.from_user.id].append(echo.message_id)


# ==========================Сохранить уведомление в БД (инлайн кнопка)==================================================
async def save_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на нажатие инлайн кнопки "сохранить".
    """
    await state.finish()
    db.add_info_to_notification([tuple(notification_dict[callback.from_user.id])])
    text = '\n'.join(['Уведомление сохранено!\n', str(notification_dict[callback.from_user.id])])
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=message_id_dict[callback.from_user.id].pop(),
                                text=text)
    await callback.answer('Уведомление сохранено!')


# ==========================Загрузка данных в БД из exel==================================================
@check_permission
async def set_file(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для запроса файла exel у пользователя
    """
    await message.reply('Прикрепите exel файл\n(не более 20 Мб!)', reply_markup=inline_cancel_keyboard)
    await state.set_state(FSM_admin.get_file_state.state)


@log
async def save_file(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер позволяющий загрузить данные из exel в БД
    Комментарий "*d" к отправляемому фалу позволяет предварительно отчистить БД
    """
    if message.document.mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        file_info = await bot.get_file(message.document.file_id)
        pth = path.join(path.curdir, 'documents', message.document.file_name)
        await bot.send_chat_action(message.chat.id, types.chat.ChatActions.UPLOAD_DOCUMENT)
        await bot.download_file(file_info.file_path, pth)
        await sleep(1)
        await message.reply('Файл успешно сохранен!\
                            \nЗаписываю данные в БД...')
        match message.caption:
            case str(message.caption) if message.caption.lower() == '*d':
                db.clean_table()
        write_from_xlsx_to_db(message.document.file_name)
        await message.reply('Данные успешно записаны в БД')
        await state.finish()
        if path.isfile(pth):
            remove(pth)
    else:
        await if_not_document(message)


async def if_not_document(message: types.Message):
    await message.reply('Пожалуйста отправьте файл exel!')


# ==========================Загрузка данных в exel из БД==================================================
@check_permission
@log
async def get_file(message: types.Message) -> None:
    """
    Хендлер формирующий exel файл с данными из БД и отправляющий его пользователю
    """
    await message.reply('Формируем xlsx файл...')
    write_from_db_to_xlsx()
    pth = path.join(path.curdir, 'documents', 'DataBase.xlsx')
    fail = InputFile(pth)
    await bot.send_chat_action(message.chat.id, types.chat.ChatActions.UPLOAD_DOCUMENT)
    await sleep(1)
    await bot.send_document(chat_id=message.chat.id, document=fail)
    if path.isfile(pth):
        remove(pth)


# ================================================================================================
def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(help_admin, commands=['help_admin'])
    dp.register_message_handler(alert, commands=['alert'])
    dp.register_message_handler(change_notification_time, commands=['change_time'])
    dp.register_message_handler(set_notification_time, state=FSM_admin.get_new_notification_time)
    dp.register_message_handler(fire_admin, commands=['fire_admin'])
    dp.register_message_handler(set_fire_admin, state=FSM_admin.fire_admin_state)
    dp.register_message_handler(change_password, commands=['change_password'])
    dp.register_message_handler(set_new_password, state=FSM_admin.change_password_state)
    dp.register_message_handler(get_admin_list, commands=['admin_list'])
    dp.register_message_handler(set_file, commands=['add_db'])
    dp.register_message_handler(save_file, state=FSM_admin.get_file_state, content_types=['document'])
    dp.register_message_handler(if_not_document, state=FSM_admin.get_file_state,
                                content_types=['text', 'photo', 'sticker', 'video'])
    dp.register_message_handler(get_file, commands=['get_db'])
    dp.register_message_handler(add_notification, commands=['add_note'])
    dp.register_message_handler(add_employee_id, state=FSM_admin.add_employee_id_state)
    dp.register_message_handler(add_date, state=FSM_admin.add_date_state)
    dp.register_message_handler(add_text, state=FSM_admin.add_note_state)
    dp.register_callback_query_handler(save_call, Text(equals='save'), state=FSM_admin.add_note_state)
