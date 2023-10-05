from aiogram.dispatcher import Dispatcher
from classes import FsmAdmin, FsmUser
from aiogram.dispatcher.filters import Text

from .cancel import cancel_call
from handlers.admin import *
from handlers.user import *


def register_general_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(cancel_call, Text(equals='cancel'), state='*')


def register_user_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=['start'])
    dp.register_message_handler(help_user, commands=['help'])
    dp.register_message_handler(get_employee_id, commands=['change_id'])
    dp.register_message_handler(set_employee_id, state=FsmUser.get_employee_id_from_start_state)
    dp.register_message_handler(set_employee_id, state=FsmUser.get_employee_id_state)
    dp.register_message_handler(get_full_name, commands=['change_name'])
    dp.register_message_handler(set_full_name, state=FsmUser.get_full_name_state)
    dp.register_message_handler(get_admin, commands=['get_admin'])
    dp.register_message_handler(set_admin, state=FsmUser.get_admin_state)
    dp.register_message_handler(notification, commands=['notifications'])


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(help_admin, commands=['help_admin'])
    dp.register_message_handler(change_notification_time, commands=['change_time'])
    dp.register_message_handler(set_notification_time, state=FsmAdmin.get_new_notification_time)
    dp.register_message_handler(fire_admin, commands=['fire_admin'])
    dp.register_message_handler(set_fire_admin, state=FsmAdmin.fire_admin_state)
    dp.register_message_handler(change_password, commands=['change_password'])
    dp.register_message_handler(set_new_password, state=FsmAdmin.change_password_state)
    dp.register_message_handler(get_admin_list, commands=['admin_list'])
    dp.register_message_handler(set_file, commands=['add_db'])
    dp.register_message_handler(save_file, state=FsmAdmin.get_file_state, content_types=['document'])
    dp.register_message_handler(if_not_document, state=FsmAdmin.get_file_state,
                                content_types=['text', 'photo', 'sticker', 'video'])
    dp.register_message_handler(get_file, commands=['get_db'])
    dp.register_message_handler(add_notification, commands=['add_note'])
    dp.register_message_handler(add_employee_id, state=FsmAdmin.add_employee_id_state)
    dp.register_message_handler(add_date, state=FsmAdmin.add_date_state)
    dp.register_message_handler(add_text, state=FsmAdmin.add_note_state)
    dp.register_callback_query_handler(continue_call, Text(equals='continue'), state='*')
    dp.register_callback_query_handler(save_call, Text(equals='save'), state=FsmAdmin.add_note_state)


def register_handlers(dp: Dispatcher) -> None:
    register_general_handlers(dp)
    register_admin_handlers(dp)
    register_user_handlers(dp)
