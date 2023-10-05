def start_message_generator(name: str, start: bool = True) -> str:
    """
    Функция генерирующая сообщение для пользователя при командах start и help
    """
    helper_user_message = {
        '/help': 'вызвать сообщение с подсказками команд',
        '/change_id': 'изменить табельный номер',
        '/change_name': 'изменить ФИО',
        '/notifications': 'запросить уведомления',
    }

    text_message = f'Привет, {name} 👋!\
                    \nЯ бот который будет напоминать тебе о запланированных задачах!\n\
                    \n⚙ Ты можешь управлять мной с помощью следующих команд:\n'

    for command, description in helper_user_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    if start:
        text_message += '\n\n<b>Для подключения к системе оповещений, пожалуйста, введи свой <u>табельный ' \
                        'номер</u>:</b> '

    return text_message


def admin_message_generator() -> str:
    """
    Функция генерирующая сообщение для пользователя при получении статуса администратора
    """
    helper_admin_message = {
        '/help_admin': 'вызвать сообщение с подсказками',
        '/change_time': 'изменить время рассылки',
        '/change_password': 'изменить пароль',
        '/admin_list': 'получить список администраторов',
        '/fire_admin': 'лишить пользователя прав администратора',
        '/add_note': 'добавить уведомление в базу данных',
        '/add_db': 'добавить уведомления в базу данных из xlsx таблицы (*d в комментарии к файлу предварительно '
                   'отчистит базу данных)',
        '/get_db': 'получить весь список уведомлений из базы данных в виде xlsx таблицы',
    }

    text_message = f'<b>Поздравляю, вам доступны команды администратора! 🔓</b>\n'

    for command, description in helper_admin_message.items():
        text_message = '\n'.join([text_message, f'{command} - {description}'])

    return text_message