import asyncio
import logging
from freeGPTFix import Client
import requests

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton
from aiogram.client.session.aiohttp import AiohttpSession

# Bot tokeningizni kiriting
TOKEN = "7285989682:AAHLE-c_8uflbHjAKPfEORcPSjYRr4HTPc0"
API_KEY = "e7aeeb0423d64b27462d4882284c864f"
CHANNEL_USERNAME = "android_developer_20"  # Telegram kanali username

# Dispatcher yaratamiz
dp = Dispatcher()



async def is_user_subscribed_to_channel(bot: Bot, user_id: int) -> bool:
    """
    Foydalanuvchining Telegram kanaliga obuna bo'lganligini tekshirish.
    """
    try:
        member = await bot.get_chat_member(chat_id=f"@{CHANNEL_USERNAME}", user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception as e:
        logging.error(f"Obuna tekshiruvida xatolik: {e}")
        return False


@dp.message(CommandStart())
async def command_start_handler(message: Message, bot: Bot) -> None:
    """
    Start komandasi uchun ishlovchi handler.
    """
    user_id = message.from_user.id
    username = message.from_user.username or "Foydalanuvchi"

    # "Weather" tugmasi qo'shilgan menyu
    weather_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Weather")],
        ],
        resize_keyboard=True
    )

    if await is_user_subscribed_to_channel(bot, user_id):
        await message.answer(
            f"Salom, @{username}! Botdan foydalanishingiz mumkin. Savollaringizni yozing.",
            reply_markup=weather_keyboard,
        )
    else:
        # Obuna bo'lish tugmalari bilan keyboard
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Telegram kanalga obuna bo'lish",
                        url=f"https://t.me/{CHANNEL_USERNAME}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Tasdiqlash",
                        callback_data="confirm_subscription"
                    )
                ]
            ]
        )
        await message.answer(
            f"Salom, @{username}! Botdan foydalanish uchun avval Telegram kanalimizga obuna bo'ling va 'Tasdiqlash' tugmasini bosing.",
            reply_markup=keyboard,
        )


@dp.callback_query(lambda c: c.data == "confirm_subscription")
async def confirm_subscription_handler(callback_query: CallbackQuery, bot: Bot):
    """
    Tasdiqlash tugmasi bosilganda ishlovchi handler.
    """
    user_id = callback_query.from_user.id
    username = callback_query.from_user.username

    if await is_user_subscribed_to_channel(bot, user_id):
        await callback_query.message.edit_text(
            f"@{username}, obuna muvaffaqiyatli tasdiqlandi! Endi botdan foydalanishingiz mumkin."
        )
    else:
        await callback_query.answer(
            "Siz hali Telegram kanalimizga obuna bo'lmagansiz.",
            show_alert=True
        )


regions = {
    "toshkent": "Toshkent",
    "samarkand": "Samarqand",
    "bukhara": "Buxoro",
    "andijan": "Andijon",
    "fergana": "Farg'ona",
    "namangan": "Namangan",
    "qashqadaryo": "Qashqadaryo",
    "surxondaryo": "Surxondaryo",
    "khorezm": "Xorazm",
    "navoiy": "Navoiy",
    "karakalpakstan": "Qoraqalpog'iston"
}

# OpenWeatherMap API'dan ob-havo ma'lumotlarini olish
def get_weather(region: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={region}&appid={API_KEY}&units=metric&lang=uz"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return "❌ Ob-havo ma'lumotlari topilmadi."

    main = data["main"]
    weather = data["weather"][0]
    temp = main["temp"]
    description = weather["description"]
    wind_speed = data["wind"]["speed"]
    city_name = data["name"]

    weather_info = (
        f"📍 {city_name} shahrining ob-havo ma'lumoti:\n\n"
        f"🌡 Hozirgi harorat: {temp}°C\n"
        f"☀️ Holat: {description.capitalize()}\n"
        f"💨 Shamol: {wind_speed} m/s"
    )
    return weather_info

@dp.message(lambda message: message.text.lower() == "weather")
async def weather_menu_handler(message: Message):
    """
    "Weather" tugmasi bosilganda ishlovchi handler.
    """
    regions_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Toshkent", callback_data="weather_toshkent"),
                InlineKeyboardButton(text="Samarqand", callback_data="weather_samarkand"),
            ],
            [
                InlineKeyboardButton(text="Buxoro", callback_data="weather_bukhara"),
                InlineKeyboardButton(text="Andijon", callback_data="weather_andijan"),
            ],
            [
                InlineKeyboardButton(text="Farg'ona", callback_data="weather_fergana"),
                InlineKeyboardButton(text="Namangan", callback_data="weather_namangan"),
            ],
            [
                InlineKeyboardButton(text="Qashqadaryo", callback_data="weather_qashqadaryo"),
                InlineKeyboardButton(text="Surxondaryo", callback_data="weather_surxondaryo"),
            ],
            [
                InlineKeyboardButton(text="Xorazm", callback_data="weather_khorezm"),
                InlineKeyboardButton(text="Navoiy", callback_data="weather_navoiy"),
            ],
            [
                InlineKeyboardButton(text="Qoraqalpog'iston", callback_data="weather_karakalpakstan"),
            ],
        ]
    )
    await message.answer("Viloyatni tanlang:", reply_markup=regions_keyboard)

@dp.callback_query(lambda c: c.data.startswith("weather_"))
async def weather_handler(callback_query: CallbackQuery):
    """
    Viloyat ob-havosini ko'rsatish uchun handler.
    """
    region_key = callback_query.data.split("_")[1]  # Viloyatning kalitini olish
    region_name = regions.get(region_key, "Shahar topilmadi")  # Viloyat nomini olish

    if region_name == "Shahar topilmadi":
        await callback_query.message.edit_text("Siz asosiy menudasiz")
        return

    weather_info = get_weather(region_name)  # OpenWeatherMap API'dan ob-havo ma'lumotlarini olish
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Orqaga", callback_data="weather_menu")]
        ]
    )
    await callback_query.message.edit_text(weather_info, reply_markup=keyboard)
    await callback_query.answer()  # Callbackni yakunlash




@dp.message()
async def ai_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username

    if not await is_user_subscribed_to_channel(Bot(token=TOKEN), user_id):
        await message.answer(
            f"@{username}, iltimos avval Telegram kanalimizga obuna bo'ling va /start buyrug'ini qayta yuboring."
        )
        return

    prompt = message.text
    try:
        # freeGPTFix orqali so'rov yuborish
        resp = Client.create_completion("gpt4", prompt)

        # Javobni formatlash
        formatted_response = f"""
🤖 **Bot javobi**:
===================
{resp}

📌 Iltimos, qo'shimcha savollaringiz bo'lsa yozing!
"""
        await message.answer(formatted_response, parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"🤖: Xato yuz berdi: {e}")




async def main():
    """Asosiy botni ishga tushirish funksiyasi."""
    logging.basicConfig(level=logging.INFO)

    # Bot obyektini to'g'ri konfiguratsiya qilamiz
    bot = Bot(token=TOKEN, session=AiohttpSession())

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
