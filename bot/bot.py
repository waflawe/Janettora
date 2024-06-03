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

logger.add(".logs/bot-debug.log", level="DEBUG", catch=True, filter=bot_utils.debug_only)

bot = Bot(config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_NUMBER)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    is_registered = utils.register_user_in_databases(message.from_user.id)
    if is_registered:
        logger.debug(f"User: {message.from_user.id} success registered.")
    await message.answer(f"Добрый день, @{message.from_user.username}!\n"
                         f"\n"
                         f"Это бот для тренеровки словарного запаса английского языка. "
                         f"Я предлагаю слово на английском и даю варианты ответов на русском, "
                         f"ваша задача - угадать правильный перевод. Давайте начинать тренироваться!",
                         reply_markup=keyboards.main_kb)


@dp.message(F.text == "Тренировка")
async def start_training_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    english, options, correct_option_id, open_period = await bot_utils.get_random_quiz(telegram_id)
    logger.debug(f"Success get random quiz for: {telegram_id} user.")
    message = await message.reply_poll(
        question=f"Как переводится слово {english}?",
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False,
        open_period=open_period
    )
    logger.debug(
        f"Send quiz: {message.poll.id}. Word: {english}, translation: {options[correct_option_id]}, "
        f"quiz open period: {open_period}."
    )
    await redis.set(f"{message.poll.id}", correct_option_id, open_period)
    logger.debug(f"Set correct option id in redis for: {message.poll.id} poll.")
    await bot_utils.check_quiz_completion(telegram_id, message.poll)


@dp.message(F.text == "Настройки")
async def settings_handler(message: Message) -> None:
    settings = utils.get_user_settings(message.from_user.id)
    logger.debug(f"Success get SETTINGS for: {message.from_user.id} user.")
    await message.answer("Настройки вашего пользователя:", reply_markup=keyboards.settings_kb(settings))


@dp.callback_query(F.data == "change_qac")
async def change_qac_handler(callback: CallbackQuery) -> None:
    bot_utils.change_quiz_answers_count(callback.from_user.id)
    logger.debug(f"Success change quiz answers count for: {callback.from_user.id} user.")
    await bot_utils.send_updated_settings_keyboard_by_callback(callback)


@dp.callback_query(F.data == "change_wpos")
async def change_wpos_handler(callback: CallbackQuery) -> None:
    bot_utils.change_words_part_of_speech(callback.from_user.id)
    logger.debug(f"Success change words part of speech setting for: {callback.from_user.id} user.")
    await bot_utils.send_updated_settings_keyboard_by_callback(callback)


@dp.message(F.text == "Статистика")
async def statistics_handler(message: Message) -> None:
    statistics = utils.get_user_statistics(message.from_user.id)
    logger.debug(f"Success get STATISTICS for: {message.from_user.id} user.")
    cor_to_incor = await bot_utils.get_cor_to_incor(statistics)
    logger.debug(f"Success get cor/incor STATISTICS for: {message.from_user.id} user.")
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
    await bot_utils.quiz_answer_check(
        poll_answer.user.id,
        poll_answer.poll_id,
        redis=redis,
        answer_id=poll_answer.option_ids[0]
    )


@dp.message()
async def echo(message: Message) -> None:
    logger.debug(f"Uknown command: {message.text}.")
    await message.answer("К сожалению, я не знаю такой команды :(")


async def main() -> None:
    utils.recreate_settings_and_statistics_model()
    await bot.delete_webhook(drop_pending_updates=True)
    logger.debug(
        f"Janettora starts with next parameters: DEBUG={bool(config.DEBUG)} REDIS_HOST={config.REDIS_HOST} "
        f"REDIS_PORT={config.REDIS_PORT} REDIS_DB_NUMBER={config.REDIS_DB_NUMBER} DB_NAME={config.DB_NAME} "
        f"DB_HOST={config.DB_HOST} DB_PORT={config.DB_PORT}"
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
