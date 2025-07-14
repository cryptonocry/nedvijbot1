from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os

# Используй переменные окружения в Railway
TOKEN = os.getenv("BOT_TOKEN", "7665240651:AAHbJ4fBrNQxwcLFO-J1KEHGLTe18q4CaQ4")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

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

# Кнопки навигации
def navigation_buttons(section, index, total):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if index == 0:
        keyboard.add(InlineKeyboardButton("➡️ Вперёд", callback_data=f"{section}_{index+1}"))
    elif index == total - 1:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"{section}_{index-1}"))
    else:
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{section}_{index-1}"),
            InlineKeyboardButton("➡️ Вперёд", callback_data=f"{section}_{index+1}")
        )

    keyboard.add(InlineKeyboardButton("↩️ Возврат в меню", callback_data="menu"))
    return keyboard

# Контент по разделам
section_messages = {
    "complex": [
        ("Жилой комплекс 'Сокол': стиль и комфорт", "media/complex1.jpg"),
        ("Панорама двора", "media/complex2.jpg"),
        ("Современный фасад и архитектура", "media/complex3.jpg")
    ],
    "district": [
        ("Район Сокол — элитное прошлое и будущее", "media/district1.jpg"),
        ("Инфраструктура на высоте", "media/district2.jpg"),
        ("Зелёные зоны и парки поблизости", "media/district3.jpg")
    ],
    "apartment": [
        ("Планировка квартиры 72м²", "media/apartment1.jpg"),
        ("Кухня-гостиная в стиле минимализм", "media/apartment2.jpg"),
        ("Просторная спальня с видом", "media/apartment3.jpg")
    ]
}

# Любое сообщение — главное меню
@dp.message_handler()
async def handle_any_message(message: types.Message):
    await message.answer("Выберите интересующий раздел:", reply_markup=main_menu())

# Обработка всех кнопок
@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if data == "menu":
        await bot.send_message(user_id, "Главное меню:", reply_markup=main_menu())

    elif data == "visit":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("📞 Позвонить: +79993332211", url="tel:+79993332211"),
            InlineKeyboardButton("✉️ Написать в Telegram", url="https://t.me/vitalllx"),
            InlineKeyboardButton("↩️ Возврат в меню", callback_data="menu")
        )
        await bot.send_message(user_id, "Для уточнения информации вы можете:", reply_markup=keyboard)

    elif "_" in data:
        section, index = data.split("_")
        index = int(index)
        if section in section_messages:
            text, image_path = section_messages[section][index]
            with open(image_path, "rb") as photo:
                keyboard = navigation_buttons(section, index, len(section_messages[section]))
                await bot.send_photo(user_id, photo=photo, caption=text, reply_markup=keyboard)
        else:
            await bot.send_message(user_id, "Раздел в разработке.", reply_markup=main_menu())
        await callback_query.answer()

    else:
        await bot.send_message(user_id, "Раздел в разработке.", reply_markup=main_menu())
        await callback_query.answer()

# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp)
