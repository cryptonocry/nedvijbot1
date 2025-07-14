from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "280665761"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Память: кто оставляет заявку
awaiting_input = {}

# Главное меню
def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏢 Жилой комплекс", callback_data="complex_0"),
        InlineKeyboardButton("🌍 Район", callback_data="district_0"),
        InlineKeyboardButton("🏠 Квартира", callback_data="apartment_0"),
        InlineKeyboardButton("🎥 Видеообзор", callback_data="video"),
        InlineKeyboardButton("🖼️ Визуализация", callback_data="viz"),
        InlineKeyboardButton("📅 Запись на просмотр", callback_data="visit"),
        InlineKeyboardButton("👥 Команда проекта", callback_data="team"),
        InlineKeyboardButton("🤝 Партнёр проекта", callback_data="partner"),
    )
    return keyboard

def navigation_buttons(section, index, total):
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton("⬅️ Назад!", callback_data=f"{section}_{index-1}"))
    if index < total - 1:
        buttons.append(InlineKeyboardButton("➡️ Вперёд", callback_data=f"{section}_{index+1}"))
    buttons.append(InlineKeyboardButton("↩️ В меню", callback_data="menu"))
    return InlineKeyboardMarkup().add(*buttons)

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
    user_id = callback_query.from_user.id

    if data == "menu":
        await bot.send_message(user_id, "Главное меню:", reply_markup=main_menu())
    elif data == "visit":
        awaiting_input[user_id] = True
        await bot.send_message(user_id, "Введите свои данные для записи:")
    elif "_" in data:
        section, index = data.split("_")
        index = int(index)
        if section in section_messages:
            text, image_path = section_messages[section][index]
            with open(image_path, "rb") as photo:
                keyboard = navigation_buttons(section, index, len(section_messages[section]))
                await bot.send_photo(user_id, photo=photo, caption=text, reply_markup=keyboard)
        await callback_query.answer()
    else:
        await bot.send_message(user_id, f"Раздел: {data} (контент в разработке)", reply_markup=main_menu())
        await callback_query.answer()

@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def handle_user_input(message: types.Message):
    user_id = message.from_user.id
    if awaiting_input.get(user_id):
        text = f"Заявка от @{message.from_user.username or 'без_username'}:\n{message.text}"
        await bot.send_message(ADMIN_ID, text)
        await message.answer("Спасибо! Мы получили ваше сообщение.", reply_markup=main_menu())
        awaiting_input.pop(user_id)
    else:
        await message.answer("Пожалуйста, выберите раздел из меню.", reply_markup=main_menu())

if __name__ == "__main__":
    executor.start_polling(dp)
а
