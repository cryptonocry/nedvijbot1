from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import datetime
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "280665761"))
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Заявки Telegram")
SHEET_NAME = os.getenv("SHEET_NAME", "Лист1")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class GalleryState(StatesGroup):
    viewing = State()

# Авторизация в Google Sheets
import json

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    json_creds = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not json_creds:
        raise Exception("GOOGLE_CREDENTIALS_JSON not set")
    creds_dict = json.loads(json_creds)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet


def main_menu(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("\U0001F3E2 Жилой комплекс", callback_data="complex"),
        InlineKeyboardButton("\U0001F30D Район", callback_data="district"),
        InlineKeyboardButton("\U0001F3E0 Квартира", callback_data="apartment"),
        InlineKeyboardButton("\U0001F4FD Видеообзор", callback_data="video"),
        InlineKeyboardButton("\U0001F5BC Визуализация", callback_data="viz"),
        InlineKeyboardButton("\U0001F4C5 Запись на просмотр", callback_data="visit"),
        InlineKeyboardButton("\U0001F465 Команда проекта", callback_data="team"),
        InlineKeyboardButton("\U0001F91D Партнёр проекта", callback_data="partner"),
    )
    if user_id == ADMIN_ID:
        keyboard.add(InlineKeyboardButton("\U0001F4EC Заявки", callback_data="show_requests"))
    return keyboard

nav_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton("\u21A9\uFE0F В меню", callback_data="menu")
)

section_messages = {
    "complex": [
        ("Жилой комплекс 'Сокол': стиль и комфорт", "media/complex1.jpg"),
        ("Панорама двора", "media/complex2.jpg")
    ],
    "district": [
        ("Район Сокол — элитное прошлое и будущее", "media/district1.jpg"),
        ("Инфраструктура на высоте", "media/district2.jpg")
    ],
    "apartment": [
        ("Планировка квартиры 72м²", "media/apartment1.jpg"),
        ("Кухня-гостиная в стиле минимализм", "media/apartment2.jpg")
    ]
}

@dp.message_handler(commands=["start"])
async def start(msg: types.Message):
    await msg.answer("Выберите интересующий раздел:", reply_markup=main_menu(msg.from_user.id))

@dp.callback_query_handler(lambda c: c.data in section_messages)
async def gallery_start(callback_query: types.CallbackQuery, state: FSMContext):
    section = callback_query.data
    await state.update_data(section=section, index=0)
    await GalleryState.viewing.set()
    await send_gallery_item(callback_query.from_user.id, section, 0)
    await callback_query.answer()

async def send_gallery_item(user_id, section, index):
    items = section_messages[section]
    text, image_path = items[index]
    nav = InlineKeyboardMarkup()
    if index > 0:
        nav.insert(InlineKeyboardButton("⏮ Назад", callback_data="prev_img"))
    if index < len(items) - 1:
        nav.insert(InlineKeyboardButton("⏭ Вперёд!", callback_data="next_img"))
    nav.add(InlineKeyboardButton("↩️ В меню!", callback_data="menu"))
    with open(image_path, "rb") as photo:
        await bot.send_photo(user_id, photo=photo, caption=text, reply_markup=nav)

@dp.callback_query_handler(lambda c: c.data in ["next_img", "prev_img"], state=GalleryState.viewing)
async def gallery_nav(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    section = data["section"]
    index = data["index"]
    if callback_query.data == "next_img":
        index += 1
    else:
        index -= 1
    await state.update_data(index=index)
    await send_gallery_item(callback_query.from_user.id, section, index)
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "menu", state="*")
async def back_to_menu(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(callback_query.from_user.id, "Выберите интересующий раздел:", reply_markup=main_menu(callback_query.from_user.id))
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "visit")
async def visit_handler(callback_query: types.CallbackQuery):
    await bot.send_message(callback_query.from_user.id, "Введите свои данные для записи:")
    await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data == "show_requests")
async def show_requests(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_ID:
        try:
            sheet = get_sheet()
            data = sheet.get_all_values()
            if len(data) <= 1:
                await bot.send_message(user_id, "Пока нет заявок.")
            else:
                preview = "\n\n".join([f"{row[0]} — {row[2]}\n{row[1]}" for row in data[1:]])
                await bot.send_message(user_id, f"\U0001F4EC Все заявки:\n\n{preview[:4000]}")
        except Exception as e:
            await bot.send_message(user_id, f"Ошибка чтения таблицы: {e}")
    else:
        await bot.send_message(user_id, "Эта функция доступна только админу.")
    await callback_query.answer()

@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def handle_user_input(message: types.Message):
    username = message.from_user.username or "без_username"
    date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = message.text
    try:
        sheet = get_sheet()
        sheet.append_row([f"@{username}", text, date_str])
        await bot.send_message(ADMIN_ID, f"Новая заявка от @{username}:\n{text}\n🕓 {date_str}")
    except Exception as e:
        await message.answer("Ошибка при сохранении заявки, попробуйте позже.")
        print("Google Sheets Error:", e)
        return
    await message.answer("Спасибо! Мы получили ваше сообщение.", reply_markup=main_menu(message.from_user.id))

if __name__ == "__main__":
    executor.start_polling(dp)
