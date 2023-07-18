from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("stop", "Закончить анкету (с сохранением)"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("cancel", "Отмена"),

    ])
