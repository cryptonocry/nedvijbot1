from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from aiogram.utils import executor
import os
import datetime

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "280665761"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Главное меню (с проверкой админа)
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

# Навигационная клавиатура
nav_menu = InlineKeyboardMarkup().add(
    InlineKeyboardButton("↩️ В меню", callback_data="menu")
)

# Контент по разделам
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
            if not os.path.exists("requests.txt"):
                await bot.send_message(user_id, "Пока нет заявок.")
            else:
                with open("requests.txt", "r", encoding="utf-8") as f:
                    content = f.read()

                preview = content if len(content) <= 4000 else content[-4000:]  # Telegram ограничение
                await bot.send_message(user_id, f"📬 Все заявки:\n\n{preview}")
                await bot.send_document(user_id, InputFile("requests.txt"))
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
    text = f"Заявка от @{username}:\n{message.text}"

    # Сохранение в файл
    with open("requests.txt", "a", encoding="utf-8") as f:
        f.write(f"[{date_str}] {text}\n")

    # Отправка админу
    try:
        await bot.send_message(ADMIN_ID, f"{text}\n🕓 {date_str}")
    except Exception as e:
        print(f"Ошибка при отправке админу: {e}")

    await message.answer("Спасибо! Мы получили ваше сообщение.", reply_markup=main_menu(message.from_user.id))

if __name__ == "__main__":
    executor.start_polling(dp)
