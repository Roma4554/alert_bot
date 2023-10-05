from re import search

from aiogram import types
from aiogram.dispatcher import FSMContext

import db
from create_bot import bot
from utility.decorators import check_permission
from classes import FsmAdmin, Notification
from utility.cleaner import cleaner, message_id_dict, notification_dict
from utility import search_employee_id
from keyboards import inline_cancel_keyboard, inline_save_notification_keyboard, inline_next_keyboard


time_pattern = r'([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$'
date_pattern = r'^(?:0[1-9]|[12]\d|3[01])\.(?:0[1-9]|1[012])\.(?:[12]\d{3})$'
password_pattern = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?!.*[\s#`~"\'\.\+\-\\\/\*$%№@;:^&\*\=]).*$'


@check_permission
async def add_notification(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер для добавления оповещения пользователя
    """
    await message.reply('Введите <b>табельный номер</b> пользователя или его <b>инициалы</b> (Иванов И.И):',
                        reply_markup=inline_cancel_keyboard,
                        parse_mode=types.ParseMode.HTML)

    notification_dict[message.from_user.id] = list()
    await state.set_state(FsmAdmin.add_employee_id_state.state)


async def add_employee_id(message: types.Message, state: FSMContext) -> None:
    """
    Хендлер сохраняющий табельный номер и запрашивающий дату оповещения:
    """
    if message.text.lower() == 'all':
        employees_id = db.get_employee_id_dict().keys()

        for employee_id in employees_id:
            set_notification_in_notification_dict(message, employee_id, check=False)

        echo = await message.reply('Для оповещения выбраны все пользователи!\nНажмите кнопку <b>"Продолжить"</b>',
                                   reply_markup=inline_next_keyboard,
                                   parse_mode=types.ParseMode.HTML)
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])
        await state.finish()
        return

    try:
        employee_id = search_employee_id(message)
        set_notification_in_notification_dict(message, employee_id)
        echo = await message.reply('Добавьте еще пользователя или нажмите кнопку <b>"Продолжить"</b>',
                                   reply_markup=inline_next_keyboard,
                                   parse_mode=types.ParseMode.HTML)
    except (KeyError, ValueError) as ex:
        argument = ex.args
        echo = await message.reply(*argument)
    finally:
        message_id_dict[message.from_user.id].extend([message.message_id, echo.message_id])


def set_notification_in_notification_dict(message: types.Message, employee_id: str, check: bool = True) -> None:
    if check:
        note = {note.employee_id for note in notification_dict[message.from_user.id]}
        if employee_id in note:
            raise KeyError('Пользователь уже добавлен в список')
    notification = Notification()
    notification.employee_id = employee_id
    notification_dict[message.from_user.id].append(notification)


async def continue_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на нажатие инлайн кнопки "Продолжить".
    """
    if notification_dict.get(callback.from_user.id) is None:
        return

    await state.set_state(FsmAdmin.add_date_state.state)
    echo = await callback.message.reply('📅 Введите дату в формате ДД.ММ.ГГГГ:',
                                        reply_markup=inline_cancel_keyboard,
                                        parse_mode=types.ParseMode.HTML)
    message_id_dict[callback.from_user.id].append(echo.message_id)


async def add_date(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер сохраняющий дату и запрашивающий текст уведомления.
    """
    if search(date_pattern, message.text):
        split_text = message.text.split('.')[::-1]
        date = '.'.join(split_text)
        for note in notification_dict[message.from_user.id]:
            note.date = date
        await state.set_state(FsmAdmin.add_note_state.state)
        echo = await message.reply('📝 Введите текст уведомления:',
                                   reply_markup=inline_cancel_keyboard,
                                   parse_mode=types.ParseMode.HTML)
    else:
        echo = await message.reply('Некорректный формат даты! Попробуйте еще раз:')

    message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])


async def add_text(message: types.Message) -> None:
    """
    Хенделер для предварительного просмотра сообщения и его изменение
    """
    notifications = notification_dict[message.from_user.id]
    for notification in notifications:
        notification.notification = message.html_text
    text_message = 'Чтобы изменить текст, повторно отправьте сообщение!' \
                   '\nДля сохранения конечной версии, нажмите кнопку <b>"Сохранить"</b>\n' \
                   '\n<b>Предварительный просмотр:</b>'
    text_message = '\n'.join([text_message, str(notifications[0])])
    message_id_dict[message.from_user.id].append(message.message_id)
    await cleaner(message)
    echo = await message.answer(text_message,
                                reply_markup=inline_save_notification_keyboard,
                                parse_mode=types.ParseMode.HTML)
    message_id_dict[message.from_user.id].append(echo.message_id)

async def save_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на нажатие инлайн кнопки "сохранить".
    """
    await state.finish()
    notifications = map(tuple, notification_dict[callback.from_user.id])
    db.add_info_to_notification(notifications)
    await bot.edit_message_text(chat_id=callback.message.chat.id,
                                message_id=message_id_dict[callback.from_user.id].pop(),
                                parse_mode=types.ParseMode.HTML,
                                text='✔ <b>Уведомления сохранены!</b>')