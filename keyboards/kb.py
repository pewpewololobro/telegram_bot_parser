from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

b1 = KeyboardButton('/commands')
b2 = KeyboardButton('/ports')
b3 = KeyboardButton('/append')
b4 = KeyboardButton('/parse')

kbuttons = ReplyKeyboardMarkup(resize_keyboard=True)

kbuttons.row(b1,b4).row(b2,b3)