import datetime

import asyncpg
import requests
import gspread_asyncio
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import ReplyKeyboardRemove
from google.oauth2.service_account import Credentials
from data.config import BITRIX24URI

from data.config import PATH
from keyboards.default.form_keyboard import have_area_keyboard, construction_technology_keyboard, prod_line_keyboard, \
    source_of_financing_keyboard, planing_build_keyboard, skip_email_keyboard, messengers_list_keyboard, start_keyboard
from loader import dp


def get_scoped_credentials(path: str):
    creds = Credentials.from_service_account_file(path)

    def prepare_scoped_credentials():
        return creds.with_scopes(
            ["https://spreadsheets.google.com/feeds", 'https://www.googleapis.com/auth/spreadsheets',
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
        )

    return prepare_scoped_credentials


async def create_spreadsheet(client, spreadsheet_name) -> gspread_asyncio.AsyncioGspreadSpreadsheet:
    spreadsheet = await client.create(spreadsheet_name)
    spreadsheet = await client.open_by_key(spreadsheet.id)
    return spreadsheet


async def add_worksheet(async_spreadsheet: gspread_asyncio.AsyncioGspreadSpreadsheet, worksheet_name):
    worksheet = await async_spreadsheet.add_worksheet(worksheet_name, 500, 500)
    worksheet = await async_spreadsheet.worksheet(worksheet.title)
    return worksheet


@dp.message_handler(Command("cancel"), state="*")
@dp.message_handler(text="Отмена", state="*")
async def cancel(message: types.Message, state: FSMContext):
    await message.answer("Отменено", reply_markup=start_keyboard)
    await state.reset_state()


@dp.message_handler(text='📝Новый лид')
@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО клиента", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Имя клиента")


@dp.message_handler(Command("stop"), state='*')
@dp.message_handler(state="Дополнительные комментарии")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    if message.text == "/stop":
        comment = ""
    else:
        comment = message.text
    await state.update_data(comment=comment)

    today = datetime.date.today()
    data = await state.get_data()
    await message.answer(f"1. {message.from_user.full_name}\n"
                         f"2. {today.strftime('%d.%m.%y')}\n"
                         f"3. {data.get('client_name')}\n"
                         f"4. {data.get('phone_number')}\n"
                         f"5. {data.get('have_area')}\n"
                         f"6. {data.get('location')}\n"
                         f"7. {data.get('construction_technology')}\n"
                         f"8. {data.get('prod_line')}\n"
                         f"9. {data.get('project')}\n"
                         f"10. {data.get('date_of_starting')}\n"
                         f"11. {data.get('source_of_financing')}\n"
                         f"12. {data.get('construction_budget')}\n"

                         f"13. {data.get('email')}\n"
                         f"14. {data.get('way_of_communication')}\n"
                         f"15. {data.get('comment')}\n",
                         reply_markup=start_keyboard)
    await state.reset_state()
    spreadsheet_id = '1IYUDIj8w9RLePTBgof00mmWvXZnbtvGeuRNuyMznMN0'
    client = gspread_asyncio.AsyncioGspreadClientManager(get_scoped_credentials(PATH))  # импорт из конфига
    client = await client.authorize()
    async_spreadsheet = await client.open_by_key(spreadsheet_id)

    worksheet = await async_spreadsheet.worksheet('Лист1')
    values = [
        message.from_user.full_name,
        today.strftime('%d.%m.%y'),
        data.get('client_name'),
        data.get('phone_number'),
        data.get('have_area'),
        data.get('location'),
        data.get('construction_technology'),
        data.get('prod_line'),
        data.get('project'),
        data.get('date_of_starting'),
        data.get('source_of_financing'),
        data.get('construction_budget'),
        data.get('email'),
        data.get('way_of_communication'),
        data.get('comment'),
    ]
    await worksheet.append_row(values)

    bitrix24_fields = {
        "fields": {
            "TITLE": message.from_user.full_name,
            "NAME": data.get('client_name'),
            "STATUS_ID": "NEW",
            "ASSIGNED_BY_ID": 28,
            "CURRENCY_ID": "RUB",
            "OPPORTUNITY": data.get('construction_budget'),
            "COMMENTS": data.get('comment'),
            "UF_CRM_1690179923": data.get('construction_budget'),
            "UF_CRM_1690179895": data.get('source_of_financing'),
            "UF_CRM_1690179882": data.get('date_of_starting'),
            "UF_CRM_1690179908": data.get('project'),
            "UF_CRM_1690179854": data.get('prod_line'),
            "UF_CRM_1690179841": data.get('construction_technology'),
            "UF_CRM_1690179802": data.get('location'),
            "UF_CRM_1690179826": data.get('have_area'),
            "UF_CRM_1690179814": data.get('way_of_communication'),
            "UF_CRM_1690559724": data.get('phone_number'),
            "UF_CRM_1690559734": data.get('email'),
            "SOURCE_ID": 5,
            "UTM_SOURCE": 'tg_bots',
        },
        "params": {
            "REGISTER_SONET_EVENT": "Y"
        }
    }
    requests.post(BITRIX24URI + 'crm.lead.add.json', json=(bitrix24_fields))

@dp.message_handler(state="Имя клиента")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    client_name = message.text
    await state.update_data(client_name=client_name)
    await message.answer("Номер телефона", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Номер телефона")


@dp.message_handler(state="Номер телефона")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    phone_number = message.text
    await state.update_data(phone_number=phone_number)

    await message.answer("Наличие участка", reply_markup=have_area_keyboard)
    await state.set_state("Наличие участка")


@dp.message_handler(state="Наличие участка")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    have_area = message.text
    await state.update_data(have_area=have_area)
    await message.answer("Локация", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Локация")


@dp.message_handler(state="Локация")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    location = message.text
    await state.update_data(location=location)
    await message.answer("Технология строительства", reply_markup=construction_technology_keyboard)
    await state.set_state("Технология строительства")


@dp.message_handler(state="Технология строительства")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    construction_technology = message.text
    await state.update_data(construction_technology=construction_technology)
    await message.answer("Линейка", reply_markup=prod_line_keyboard)
    await state.set_state("Линейка")


@dp.message_handler(state="Линейка")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    prod_line = message.text
    await state.update_data(prod_line=prod_line)
    await message.answer("Проект", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Проект")


@dp.message_handler(state="Проект")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    project = message.text
    await state.update_data(project=project)
    await message.answer("Дата начала строительства", reply_markup=planing_build_keyboard)
    await state.set_state("Дата начала строительства")


@dp.message_handler(state="Дата начала строительства")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    date_of_starting = message.text
    await state.update_data(date_of_starting=date_of_starting)
    await message.answer("Источник финансирования", reply_markup=source_of_financing_keyboard)
    await state.set_state("Источник финансирования")


@dp.message_handler(state="Источник финансирования")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    source_of_financing = message.text
    await state.update_data(source_of_financing=source_of_financing)
    await message.answer("Бюджет строительства", reply_markup=ReplyKeyboardRemove())
    await state.set_state("Бюджет строительства")


@dp.message_handler(state="Бюджет строительства")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    construction_budget = message.text
    await state.update_data(construction_budget=construction_budget)

    await message.answer("Электронная почта", reply_markup=skip_email_keyboard)
    await state.set_state("Электронная почта")


@dp.message_handler(state="Электронная почта")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    email = message.text
    await state.update_data(email=email)
    await message.answer("Удобный способ коммуникации", reply_markup=messengers_list_keyboard)
    await state.set_state("Удобный способ коммуникации")


@dp.message_handler(state="Удобный способ коммуникации")
async def state_data_gsheets(message: types.Message, state: FSMContext):
    way_of_communication = message.text
    await state.update_data(way_of_communication=way_of_communication)
    await message.answer("Дополнительные комментарии", reply_markup=skip_email_keyboard)
    await state.set_state("Дополнительные комментарии")
