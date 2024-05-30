import asyncio
import random
import sys
from importlib import import_module
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.exc import IntegrityError

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
keyboards = import_module("keyboards", "bot")
utils = import_module("database.utils")

logger.add(".logs/bot.log", level="INFO")

bot = Bot(config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    try:
        utils.create_user_settings(message.from_user.id)
        utils.create_user_statistics(message.from_user.id)
    except IntegrityError:
        pass
    await message.answer(f"Добрый день, @{message.from_user.username}!"
                         f"\n"
                         f"Это бот для тренеровки словарного запаса английского языка. "
                         f"Я предлагаю слово на английском и даю варианты ответов на русском, "
                         f"ваша задача - угадать правильный перевод. Давайте начинать тренироваться!",
                         reply_markup=keyboards.main_kb)


@dp.message(F.text == "Тренировка")
async def start_training_handler(message: Message) -> None:
    settings = utils.get_user_settings(message.from_user.id)
    english, russian = utils.get_random_word(settings.words_part_of_speech)
    options = [russian]
    options.extend(
        [utils.get_random_word(settings.words_part_of_speech)[1] for _ in range(settings.quiz_answers_count-1)]
    )
    random.shuffle(options)
    await message.reply_poll(
        question=f"Как переводится слово {english}?",
        options=options,
        type="quiz",
        correct_option_id=options.index(russian),
        is_anonymous=True,
        open_period=20
    )


@dp.message(F.text == "Настройки")
async def settings_handler(message: Message) -> None:
    settings = utils.get_user_settings(message.from_user.id)
    await message.answer("Настройки вашего пользователя:", reply_markup=keyboards.settings_kb(settings))


@dp.callback_query(F.data == "change_qac")
async def change_qac_handler(callback: CallbackQuery) -> None:
    utils.change_quiz_answers_count(callback.from_user.id)
    settings = utils.get_user_settings(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=keyboards.settings_kb(settings))
    await callback.answer()


@dp.callback_query(F.data == "change_wpos")
async def change_wpos_handler(callback: CallbackQuery) -> None:
    utils.change_words_part_of_speech(callback.from_user.id)
    settings = utils.get_user_settings(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=keyboards.settings_kb(settings))
    await callback.answer()


@dp.message()
async def echo(message: Message) -> None:
    await message.answer("К сожалению, я не знаю такой команды :(")


async def main() -> None:
    utils.recreate_settings_and_statistics_model()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
