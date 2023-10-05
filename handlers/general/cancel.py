from aiogram import types
from aiogram.dispatcher import FSMContext

from utility import cleaner


async def cancel_call(callback: types.CallbackQuery, state: FSMContext) -> None:
    """
    Хенделер срабатывающий на нажатие инлайн кнопки "отмена". Прерывает работу машины состояний
    """
    cur_state = await state.get_state()
    if cur_state is None:
        return
    await state.finish()
    await cleaner(callback)
    await callback.message.answer('Команда отменена!')
    await callback.answer()
