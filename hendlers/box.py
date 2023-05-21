import datetime
import logging

from configobj import ConfigObj
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext, Dispatcher
from aiogram.utils.exceptions import BotBlocked

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
    await cleaner(callback)
    await callback.message.reply('Команда отменена')
    await callback.answer()


#==========================Функция для удаления сообщений из списка============================
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



# ==========================Рассылка оповещения=================================================
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


#==========================Функция для генерации привественного сообщения============================
def start_message_generator(name: str, start: bool = True) -> str:

    helper_user_message = {
        '/help': 'вызвать сообщение с подсказками команд',
        '/change_id': 'изменить табельный номер',
        '/change_name': 'изменить ФИО',
        '/notifications': 'запросить уведомления',
    }

    text_message = f'Привет, {name}!\
                    \nЯ бот который будет напоминать тебе о сдаче необходимых экзаменов!\n\
                    \nТы можешь управлять мной с помощью следующих команд:\n'

    for command, description in helper_user_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    if start:
        text_message += '\n\n<b>Для подключения к системе оповещений, пожалуйста, введи свой табельный номер:</b>'

    return text_message


#==========================Функция для генерации сообщения help_admin============================
def admin_message_generator() -> str:
    helper_admin_message = {
        '/help_admin': 'вызвать сообщение с подсказками',
        '/alert': 'включить рассылку уведомлений',
        '/change_time': 'изменить время рассылки',
        '/change_password': 'изменить пароль',
        '/admin_list': 'получить список администраторов',
        '/fire_admin': 'лишить пользователя прав администратора',
        '/add_note': 'добавить уведомление в базу данных',
        '/add_db': 'добавить уведомления в базу данных из xlsx таблицы (*d в комментарии к файлу предварительно '
                   'отчистит базу данных)',
        '/get_db': 'получить весь список уведомлений из базы данных в виде xlsx таблицы',
    }

    text_message = f'<b>Поздравляю, вам доступны команды администратора!</b>\n'

    for command, description in helper_admin_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    return text_message



def register_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(cancel_call, Text(equals='cancel'), state='*')