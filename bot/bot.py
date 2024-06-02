import asyncio
import sys
from importlib import import_module
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, PollAnswer
from loguru import logger
from redis.asyncio.client import Redis

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
keyboards = import_module("keyboards", "bot")
utils = import_module("database.utils")
bot_utils = import_module("utils", "bot")

logger.add(".logs/bot.log", level="INFO")

bot = Bot(config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_NUMBER)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    utils.register_user_in_databases(message.from_user.id)
    await message.answer(f"Добрый день, @{message.from_user.username}!\n"
                         f"\n"
                         f"Это бот для тренеровки словарного запаса английского языка. "
                         f"Я предлагаю слово на английском и даю варианты ответов на русском, "
                         f"ваша задача - угадать правильный перевод. Давайте начинать тренироваться!",
                         reply_markup=keyboards.main_kb)


@dp.message(F.text == "Тренировка")
async def start_training_handler(message: Message) -> None:
    english, options, correct_option_id, open_period = bot_utils.get_random_quiz(message.from_user.id)
    message = await message.reply_poll(
        question=f"Как переводится слово {english}?",
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False,
        open_period=open_period
    )
    await redis.set(f"{message.poll.id}", correct_option_id, open_period)


@dp.message(F.text == "Настройки")
async def settings_handler(message: Message) -> None:
    settings = utils.get_user_settings(message.from_user.id)
    await message.answer("Настройки вашего пользователя:", reply_markup=keyboards.settings_kb(settings))


@dp.callback_query(F.data == "change_qac")
async def change_qac_handler(callback: CallbackQuery) -> None:
    utils.change_quiz_answers_count(callback.from_user.id)
    bot_utils.send_updated_settings_keyboard_by_callback(callback)


@dp.callback_query(F.data == "change_wpos")
async def change_wpos_handler(callback: CallbackQuery) -> None:
    utils.change_words_part_of_speech(callback.from_user.id)
    bot_utils.send_updated_settings_keyboard_by_callback(callback)


@dp.message(F.text == "Статистика")
async def statistics_handler(message: Message) -> None:
    statistics = utils.get_user_statistics(message.from_user.id)
    cor_to_incor = await bot_utils.get_cor_to_incor(statistics)
    await message.answer(
        f"Вот ваша статистика за все время использования бота:\n"
        f"\n"
        f"Всего пройдено викторин: {statistics.total_quizzes}\n"
        f"Правильных ответов: {statistics.total_correct}\n"
        f"Неправильных ответов: {statistics.total_incorrect}\n"
        f"Отношение правильных ответов к неправильным: {cor_to_incor}"
    )


@dp.poll_answer()
async def quiz_answer_handler(poll_answer: PollAnswer) -> None:
    correct_option_id = await redis.get(f"{poll_answer.poll_id}")
    correct_option_id = int(correct_option_id.decode("utf-8"))
    utils.update_correct_or_incorrect_answers(
        poll_answer.user.id,
        correct_option_id == poll_answer.option_ids[0]
    )


@dp.message()
async def echo(message: Message) -> None:
    await message.answer("К сожалению, я не знаю такой команды :(")


async def main() -> None:
    utils.recreate_settings_and_statistics_model()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
