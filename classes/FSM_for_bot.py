from aiogram.dispatcher.filters.state import State, StatesGroup


class FSM_admin(StatesGroup):
    """Класс состояний для команд администратора"""
    get_new_notification_time = State()

    fire_admin_state = State()

    change_password_state = State()

    get_file_state = State()

    add_employee_id_state = State()
    add_date_state = State()
    add_note_state = State()

    add_notification_state = State()
    add_time_state = State()

class FSM_user(StatesGroup):
    """Класс состояний для пользователей"""
    get_employee_id_state = State()
    get_employee_id_from_start_state = State()
    get_admin_state = State()
    get_full_name_state = State()