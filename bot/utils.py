import random
import sys
import typing
import asyncio
from importlib import import_module
from pathlib import Path

from aiogram.types import CallbackQuery, Poll
from loguru import logger
from redis.asyncio.client import Redis

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
keyboards = import_module("keyboards", "bot")
utils = import_module("database.utils")
models = import_module("database.models")
constants = import_module("constants", "bot")

if config.DEBUG:
    logger.add(".logs/bot-debug.log", level="DEBUG", catch=True)


async def send_updated_settings_keyboard_by_callback(callback: CallbackQuery) -> None:
    """
    Sending an updated settings keyboard after updating the user settings.

    :param callback: Callback of setting changes
    """

    settings = utils.get_user_settings(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=keyboards.settings_kb(settings))
    await callback.answer()


async def get_cor_to_incor(statistics: models.UserStatistics) -> float | int:
    """
    Calculating the ratio of correct quiz answers to incorrect answers via user statistics.

    :param statistics: User UserStatistics object
    :return: Calculated ratio (maximum 2 numbers after the dot)
    """

    if statistics.total_incorrect != 0:
        return round((statistics.total_correct/statistics.total_incorrect), 2)
    else:
        return statistics.total_correct


async def get_random_quiz(telegram_id: int) -> typing.Tuple[str, typing.List, int, int]:
    """
    Create a random quiz for the user according to their settings.

    :param telegram_id: User telegram id
    :return: Tuple of English version of the generated word,
    List of answer choices, index of correct answer, quiz validity time.
    """

    settings = utils.get_user_settings(telegram_id)
    english, russian = utils.get_random_word(settings.words_part_of_speech)
    options = [russian]
    options.extend(
        [utils.get_random_word(settings.words_part_of_speech)[1] for _ in range(settings.quiz_answers_count - 1)]
    )
    random.shuffle(options)
    correct_option_id = options.index(russian)
    open_period = constants.QUIZ_ANSWER_TIME_BY_USER_ANSWERS_COUNT[settings.quiz_answers_count]

    return english, options, correct_option_id, open_period


async def quiz_answer_check(
        telegram_id: int,
        poll_id: int,
        is_correct: typing.Optional[bool] = None,
        redis: typing.Optional[Redis] = None,
        answer_id: typing.Optional[int] = None
) -> None:
    """
    Checking the answer to the quiz.

    :param telegram_id: User telegram id
    :param poll_id: Quiz id
    :param is_correct: Optional. Parameter for prematurely determining the correctness of a response
    :param redis: Optional. redis.asyncio.client.Redis object to determine if the response
    is correct inside the function.
    :param answer_id: Optional. Identifier of the response received from the user
    """

    if is_correct is None:
        correct_option_id = await redis.get(f"{poll_id}")
        correct_option_id = int(correct_option_id.decode("utf-8"))
        is_correct = correct_option_id == answer_id
    if config.DEBUG:
        logger.debug(f"Викторина {poll_id} решена {telegram_id} как {is_correct}")
    utils.update_correct_or_incorrect_answers(
        telegram_id,
        is_correct
    )


async def check_quiz_completion(telegram_id: int, poll: Poll) -> None:
    """
    Verifying that the quiz has been taken during its open period.

    :param telegram_id: User telegram id
    :param poll: Verification quiz
    """

    await asyncio.sleep(poll.open_period)
    if poll.total_voter_count == 0:
        is_correct = False
        await quiz_answer_check(telegram_id, int(poll.id), is_correct)
