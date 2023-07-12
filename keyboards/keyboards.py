from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

inline_cancel_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена',
                                                                         callback_data='cancel'))

inline_save_notification_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Сохранить',
                                                                                    callback_data='save'),
                                                               InlineKeyboardButton('Отмена',
                                                                                    callback_data='cancel'))

inline_next_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Продолжить',
                                                                       callback_data='continue'),
                                                  InlineKeyboardButton('Отмена',
                                                                       callback_data='cancel'))
