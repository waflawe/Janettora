import random
import sys
import typing
from importlib import import_module
from pathlib import Path

from aiogram.types import CallbackQuery

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

keyboards = import_module("keyboards", "bot")
utils = import_module("database.utils")
models = import_module("database.models")
constants = import_module("constants", "bot")


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
