from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

inline_cancel_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Отмена',
                                                                         callback_data='cancel'))

inline_save_notification_keyboard = InlineKeyboardMarkup().add(InlineKeyboardButton('Сохранить',
                                                                                    callback_data='save'),
                                                               InlineKeyboardButton('Отмена',
                                                                                    callback_data='cancel'))


