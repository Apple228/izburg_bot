import asyncpg
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import ReplyKeyboardRemove

from keyboards.default.form_keyboard import have_area_keyboard
from loader import dp

@dp.message_handler(text='📝Новый лид')
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО клиента", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Имя клиента")

@dp.message_handler(state="Имя клиента")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    client_name = message.text
    await state.update_data(client_name=client_name)
    await message.answer("Наличие участка", reply_markup=have_area_keyboard)
    await state.set_state("Наличие участка")

@dp.message_handler(state="Наличие участка")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    have_area = message.text
    await state.update_data(client_name=have_area)
    await message.answer("Локация", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Локация")


