from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "280665761"))
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME", "Заявки")
SHEET_NAME = os.getenv("SHEET_NAME", "Лист1")

# Авторизация в Google Sheets
def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(SHEET_NAME)
    return sheet

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

def main_menu(user_id=None):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏢 Жилой комплекс", callback_data="complex"),
        InlineKeyboardButton("🌍 Район", callback_data="district"),
        InlineKeyboardButton("🏠 Квартира", callback_data="apartment"),
        InlineKeyboardButton("🎥 Видеообзор", callback_data="video"),
        InlineKeyboardButton("🖼️ Визуализация", callback_data="viz"),
        InlineKeyboardButton("📅 Запись на просмотр", callback_data="visit"),
        InlineKeyboardButton("👥 Команда проекта", callback_data="team"),
        InlineKeyboardButton("🤝 Партнёр проекта", callback_data="partner"),
    )
    if user_id == ADMIN_ID:
        keyboard.add(InlineKeyboardButton("📬 Заявки", callback_data="show_requests"))
    return keyboard

nav_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton("↩️ В меню", callback_data="menu")
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

@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "menu":
        await bot.send_message(user_id, "Выберите интересующий раздел:", reply_markup=main_menu(user_id))

    elif data == "visit":
        await bot.send_message(user_id, "Введите свои данные для записи:")

    elif data == "show_requests":
        if user_id == ADMIN_ID:
            try:
                sheet = get_sheet()
                data = sheet.get_all_values()
                if len(data) <= 1:
                    await bot.send_message(user_id, "Пока нет заявок.")
                else:
                    preview = "\n\n".join([f"{row[0]} — {row[2]}\n{row[1]}" for row in data[1:]])
                    await bot.send_message(user_id, f"📬 Все заявки:\n\n{preview[:4000]}")
            except Exception as e:
                await bot.send_message(user_id, f"Ошибка чтения таблицы: {e}")
        else:
            await bot.send_message(user_id, "Эта функция доступна только админу.")

    elif data in section_messages:
        for text, image_path in section_messages[data]:
            with open(image_path, "rb") as photo:
                await bot.send_photo(user_id, photo=photo, caption=text)
        await bot.send_message(user_id, "↩️ Вернуться в меню", reply_markup=nav_menu)

    else:
        await bot.send_message(user_id, f"Раздел: {data} (контент в разработке)", reply_markup=nav_menu)

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
