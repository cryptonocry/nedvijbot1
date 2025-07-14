from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "280665761"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
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
    return keyboard

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
    await msg.answer("Выберите интересующий раздел:", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data

    if data == "visit":
        await bot.send_message(callback_query.from_user.id, "Введите свои данные для записи:")
    elif data in section_messages:
        for text, image_path in section_messages[data]:
            with open(image_path, "rb") as photo:
                await bot.send_photo(callback_query.from_user.id, photo=photo, caption=text)
    else:
        await bot.send_message(callback_query.from_user.id, f"Раздел: {data} (контент в разработке)")
    await callback_query.answer()

@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def handle_user_input(message: types.Message):
    text = f"Заявка от @{message.from_user.username or 'без_username'}:\n{message.text}"
    await bot.send_message(ADMIN_ID, text)
    await message.answer("Спасибо! Мы получили ваше сообщение.")

if __name__ == "__main__":
    executor.start_polling(dp)
