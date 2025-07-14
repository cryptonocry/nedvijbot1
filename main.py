from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
import os

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token="7665240651:AAHbJ4fBrNQxwcLFO-J1KEHGLTe18q4CaQ4")
dp = Dispatcher(bot)

def main_menu():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("\U0001F3E2 Жилой комплекс", callback_data="complex_0"),
        InlineKeyboardButton("\U0001F30D Район", callback_data="district_0"),
        InlineKeyboardButton("\U0001F3E0 Квартира", callback_data="apartment_0"),
        InlineKeyboardButton("\U0001F3A5 Видеообзор", callback_data="video"),
        InlineKeyboardButton("\U0001F5BC\FE0F Визуализация", callback_data="viz"),
        InlineKeyboardButton("\U0001F4C5 Запись на просмотр", callback_data="visit"),
        InlineKeyboardButton("\U0001F46E Команда проекта", callback_data="team"),
        InlineKeyboardButton("\U0001F91D Партнёр проекта", callback_data="partner"),
    )
    return keyboard

def navigation_buttons(section, index, total):
    keyboard = InlineKeyboardMarkup(row_width=2)

    if index == 0:
        # Первый слайд: только "Вперёд"
        keyboard.add(InlineKeyboardButton("➡️ Вперёд", callback_data=f"{section}_{index+1}"))
    elif index == total - 1:
        # Последний слайд: только "Назад"
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"{section}_{index-1}"))
    else:
        # Все промежуточные
        keyboard.row(
            InlineKeyboardButton("⬅️ Назад", callback_data=f"{section}_{index-1}"),
            InlineKeyboardButton("➡️ Вперёд", callback_data=f"{section}_{index+1}")
        )

    # Возврат в меню в отдельной строке
    keyboard.add(InlineKeyboardButton("↩️ Возврат в меню", callback_data="menu"))

    return keyboard


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
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✉️ Написать в Telegram", url="https://t.me/vitalllx"),
            InlineKeyboardButton("↩️ В меню", callback_data="menu")
        )
        await bot.send_message(
            user_id,
            "Для уточнения информации вы можете позвонить по номеру +79993332211 или написать нам в Telegram: @vitalllx",
            reply_markup=keyboard
        )
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

if __name__ == "__main__":
    executor.start_polling(dp)
