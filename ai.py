import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from freeGPTFix import Client

# Bot tokeningizni kiriting
TOKEN = "7285989682:AAHLE-c_8uflbHjAKPfEORcPSjYRr4HTPc0"

# Dispatcher yaratamiz
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    username = message.from_user.username  # Foydalanuvchining username'ini olish
    await message.answer(
        f"Salom, @{username}! AI botiga xush kelibsiz. Sizga nima yordam bera olaman?"
    )


# Asosiy handler, foydalanuvchidan matn olish va javob berish
@dp.message()
async def ai_handler(message: Message):
    username = message.from_user.username
    prompt = message.text  # Foydalanuvchining xabari
    try:
        # freeGPTFix orqali so'rov yuborish
        resp = Client.create_completion("gpt4", prompt)
        await message.answer(f"@{username}!\n {resp}")  # Bot orqali javobni yuborish
    except Exception as e:
        await message.answer(f"🤖: Xato yuz berdi: {e}")



async def main():
    """Asosiy botni ishga tushirish funksiyasi."""
    logging.basicConfig(level=logging.INFO)

    # Bot obyektini to'g'ri konfiguratsiya qilamiz
    bot = Bot(
        token=TOKEN,
        session=AiohttpSession(),
        default=DefaultBotProperties(parse_mode="HTML")  # Yangi usulda parse_mode
    )

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
