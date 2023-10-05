from re import search
from datetime import datetime, date, time, timedelta

from aiogram import types
from asyncio import all_tasks, create_task
from aiogram.dispatcher import FSMContext

from utility.decorators import check_permission
from keyboards import inline_cancel_keyboard
from classes import FsmAdmin
from utility.cleaner import config, message_id_dict
from utility import auto_alert, cleaner

time_pattern = r'([01]\d|2[0-3]):[0-5]\d(:[0-5]\d)?$'


@check_permission
async def change_notification_time(message: types.Message, state: FSMContext) -> None:
    await message.answer('⏰ Введите время оповещения в формате ЧЧ:ММ или ЧЧ:ММ:CC.',
                         reply_markup=inline_cancel_keyboard)
    await state.set_state(FsmAdmin.get_new_notification_time.state)


async def set_notification_time(message: types.Message, state: FSMContext) -> None:
    """
    Хенделер изменяющий время оповещения пользователя
    """
    if search(time_pattern, message.text):
        split_time = list(map(int, message.text.split(':')))
        if len(split_time) == 2:
            split_time.append(0)
        cur_date = date.today()
        new_time = time(hour=split_time[0], minute=split_time[1], second=split_time[2])
        new_datetime = datetime.combine(cur_date, new_time)
        new_datetime -= timedelta(hours=int(config['DEFAULT']['utc_different']))
        config['DEFAULT']['notification_time'] = new_datetime.strftime('%H:%M:%S')
        config.write()
        await message.reply(f'✔ <b>Время оповещения</b> успешно изменено на <u>{message.text}</u>!',
                            parse_mode=types.ParseMode.HTML)

        message_id_dict[message.from_user.id].append(message.message_id)
        await cleaner(message)
        await state.finish()

        for task in all_tasks():
            if task.get_name() == 'Auto_alert':
                task.cancel()
                create_task(auto_alert(), name='Auto_alert')
                break
    else:
        echo = await message.reply('Некорректный формат времени.\nПопробуйте еще раз!')
        message_id_dict[message.from_user.id].extend([echo.message_id, message.message_id])
