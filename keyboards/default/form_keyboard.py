from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

have_area_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                     keyboard=[
                                         [
                                             KeyboardButton(text="Есть"),
                                             KeyboardButton(text="Нет"),
                                         ]
                                     ])
