from aiogram import Dispatcher

from loader import dp
# from .big_brother import BigBrother  #вернуть
from .throttling import ThrottlingMiddleware


if __name__ == "middlewares":
    # dp.middleware.setup(BigBrother())  #вернуть
    dp.middleware.setup(ThrottlingMiddleware())
