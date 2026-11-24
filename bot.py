import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")
WEBAPP_URL = os.getenv("WEBAPP_URL")
if not TOKEN or not WEBAPP_URL:
    raise RuntimeError("Заполните BOT_TOKEN и WEBAPP_URL в .env")

bot = Bot(TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Открыть NFT-клуб", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await message.answer(
        "Добро пожаловать в NFT-клуб! Здесь бесплатный ежедневный розыгрыш NFT. "
        "CS-скинов нет — только цифровые коллекционные предметы.",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
