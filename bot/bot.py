import asyncio
from importlib import import_module
from pathlib import Path
import sys
from loguru import logger

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
keyboards = import_module("keyboards", "bot")

logger.add(".logs/bot.log", level="INFO")

bot = Bot(config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer(f"Добрый день, @{message.from_user.username}!"
                         f"\n"
                         f"Это бот для тренеровки словарного запаса английского языка. "
                         f"Я предлагаю слово на английском и даю варианты ответов на русском, "
                         f"ваша задача - угадать правильный перевод. Давайте начинать тренироваться!",
                         reply_markup=keyboards.main_kb)


@dp.message(F.text == "Тренировка")
async def start_training_handler(message: Message) -> None:
    pass


@dp.message()
async def echo(message: Message) -> None:
    await message.answer("К сожалению, я не знаю такой команды :(")


async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
