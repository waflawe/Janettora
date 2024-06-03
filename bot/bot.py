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

if config.DEBUG:
    logger.add(".logs/bot-debug.log", level="DEBUG", catch=True)

bot = Bot(config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_NUMBER)


@dp.message(CommandStart())
async def start_handler(message: Message) -> None:
    is_registered = utils.register_user_in_databases(message.from_user.id)
    if is_registered and config.DEBUG:
        logger.debug(f"Зарегестрировал {message.from_user.id}")
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
    message = await message.reply_poll(
        question=f"Как переводится слово {english}?",
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False,
        open_period=open_period
    )
    if config.DEBUG:
        logger.debug(
            f"Создал викторину {message.poll.id}. Слово {english}, перевод - {options[correct_option_id]}, "
            f"время действия виторины - {open_period}"
        )
    await redis.set(f"{message.poll.id}", correct_option_id, open_period)
    await bot_utils.check_quiz_completion(telegram_id, message.poll)


@dp.message(F.text == "Настройки")
async def settings_handler(message: Message) -> None:
    settings = utils.get_user_settings(message.from_user.id)
    await message.answer("Настройки вашего пользователя:", reply_markup=keyboards.settings_kb(settings))


@dp.callback_query(F.data == "change_qac")
async def change_qac_handler(callback: CallbackQuery) -> None:
    utils.change_quiz_answers_count(callback.from_user.id)
    if config.DEBUG:
        logger.debug(f"Количество ответов для пользователя {callback.from_user.id} изменено")
    await bot_utils.send_updated_settings_keyboard_by_callback(callback)


@dp.callback_query(F.data == "change_wpos")
async def change_wpos_handler(callback: CallbackQuery) -> None:
    utils.change_words_part_of_speech(callback.from_user.id)
    if config.DEBUG:
        logger.debug(f"Части речи слов в викторинах для пользователя {callback.from_user.id} изменены")
    await bot_utils.send_updated_settings_keyboard_by_callback(callback)


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
    await bot_utils.quiz_answer_check(
        poll_answer.user.id,
        poll_answer.poll_id,
        redis=redis,
        answer_id=poll_answer.option_ids[0]
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
