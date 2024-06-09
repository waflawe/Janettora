import asyncio
import random
import sys
import typing
from importlib import import_module
from pathlib import Path

from aiogram.types import CallbackQuery, Poll
from loguru import logger
from redis.asyncio.client import Redis
import pickle

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
keyboards = import_module("keyboards", "bot")
api = import_module("database.api")
models = import_module("database.models")
constants = import_module("constants", "bot")


def debug_only(record: typing.Mapping) -> bool:
    return record["level"].name == "DEBUG" and config.DEBUG


logger.add(".logs/bot-debug.log", level="DEBUG", catch=True, filter=debug_only)
redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_NUMBER)

########################
# PROXY METHODS TO API #
########################


async def get_user_settings(telegram_id: int) -> api.UserSettings:
    """
    Proxy method for api.get_user_settings for cache user settings and don't repeat logger message.

    :param telegram_id: User telegram id
    :return: UserSettings object with user settings
    """

    settings, from_cache = await redis.get(f"{telegram_id}:{config.CACHE_SETTINGS_VARIABLE_NAME}"), True
    if not settings:
        settings, from_cache = api.get_user_settings(telegram_id), False
        settings = pickle.dumps(settings)
        await redis.set(f"{telegram_id}:{config.CACHE_SETTINGS_VARIABLE_NAME}", settings)
    settings = pickle.loads(settings)
    logger.debug(f"Success get SETTINGS for: {telegram_id} user from cache: {from_cache}.")
    return settings


async def get_user_statistics(telegram_id: int) -> api.UserStatistics:
    """
    Prozy method for api.get_user_statistics for don't repeat logger message.

    :param telegram_id: User telegram id
    :return: UserStatistics object with user statistics
    """

    statistics = api.get_user_statistics(telegram_id)
    logger.debug(f"Success get STATISTICS for: {telegram_id} user.")
    return statistics


#####################
# SETTINGS CHANGERS #
#####################


async def change_quiz_answers_count(telegram_id: int) -> None:
    """
    Change quiz_answers_count user setting.

    :param telegram_id: User telegram id
    """

    settings = await get_user_settings(telegram_id)
    quiz_answers_count = settings.quiz_answers_count
    logger.debug(f"Quiz answers count BEFORE update: {quiz_answers_count}.")
    if quiz_answers_count+1 in api.get_quiz_answers_count_range():
        quiz_answers_count += 1
    else:
        quiz_answers_count = api.get_quiz_answers_count_range().start
    logger.debug(f"Quiz answers count AFTER update: {quiz_answers_count}.")
    api.update_user_settings(
        telegram_id=telegram_id,
        quiz_answers_count=quiz_answers_count
    )
    await redis.delete(f"{telegram_id}:{config.CACHE_SETTINGS_VARIABLE_NAME}")
    logger.debug(f"Success update SETTINGS for: {telegram_id} user.")


async def change_words_part_of_speech(telegram_id: int) -> None:
    """
    Change words_part_of_speech user setting.

    :param telegram_id: User telegram id
    """

    settings = await get_user_settings(telegram_id)
    words_part_of_speech = settings.words_part_of_speech
    logger.debug(f"Words part of speech BEFORE update: {words_part_of_speech}.")
    pos_english = list(constants.PARTS_OF_SPEECH_TRANSLATIONS.values())
    try:
        words_part_of_speech = pos_english[pos_english.index(words_part_of_speech)+1]
    except IndexError:
        words_part_of_speech = pos_english[0]
    logger.debug(f"Words part of speech AFTER update: {words_part_of_speech}.")
    api.update_user_settings(
        telegram_id=telegram_id,
        words_part_of_speech=words_part_of_speech
    )
    await redis.delete(f"{telegram_id}:{config.CACHE_SETTINGS_VARIABLE_NAME}")
    logger.debug(f"Success update SETTINGS for: {telegram_id} user.")


#######################
# STATISTICS UPDATERS #
#######################


async def update_most_used_wpos_and_qac_statistics(telegram_id: int) -> None:
    """
    Updates the statistics associated with the setting in use.

    :param telegram_id: User telegram id
    """

    statistics = await get_user_statistics(telegram_id)
    settings = await get_user_settings(telegram_id)
    mustat = statistics.most_used_wpos_and_qac
    wpos, qac = settings.words_part_of_speech, settings.quiz_answers_count
    logger.debug(f"Most used statistics: {telegram_id} user BEFORE update: {mustat}.")
    for setting in (wpos, qac):
        if mustat and setting in mustat:
            mustat[setting] += 1
        else:
            mustat = mustat if mustat else dict()
            mustat[setting] = 1
    logger.debug(f"Most used statistics: {telegram_id} user AFTER update: {mustat}.")
    api.update_user_statistics(
        telegram_id=telegram_id,
        most_used_wpos_and_qac=mustat
    )
    logger.debug(f"Success update STATISTICS for: {telegram_id} user.")


async def update_correct_or_incorrect_answers(telegram_id: int, is_correct: bool) -> None:
    """
    Update the total_correct or total_incorrect field in the user's statistics.

    :param telegram_id: User telegram id
    :param is_correct: Flag to indicate the field to be updated
    """

    statistics = await get_user_statistics(telegram_id)
    kwargs = {"telegram_id": telegram_id, "total_quizzes": statistics.total_quizzes+1}
    attr = "total_correct" if is_correct else "total_incorrect"
    kwargs[attr] = getattr(statistics, attr) + 1
    api.update_user_statistics(**kwargs)
    logger.debug(f"Success update STATISTICS for: {telegram_id} user.")


#########
# OTHER #
#########


async def send_updated_settings_keyboard_by_callback(callback: CallbackQuery) -> None:
    """
    Sending an updated settings keyboard after updating the user settings.

    :param callback: Callback of setting changes
    """

    settings = await get_user_settings(callback.from_user.id)
    await callback.message.edit_reply_markup(reply_markup=keyboards.settings_kb(settings))
    await callback.answer()


def get_cor_to_incor(statistics: models.UserStatistics) -> float | int:
    """
    Calculating the ratio of correct quiz answers to incorrect answers via user statistics.

    :param statistics: User UserStatistics object
    :return: Calculated ratio (maximum 2 numbers after the dot)
    """

    if statistics.total_incorrect != 0:
        return round((statistics.total_correct/statistics.total_incorrect), 2)
    else:
        return statistics.total_correct


def most_used_statistics_to_answer(*brackets: typing.Dict[str, str]) -> str:
    """
    Gets most used statistics in read-ready view.

    :param brackets: Statistical data pairs
    :return: Read-ready statistical data
    """

    answer = ""
    for bracket in brackets:
        answer += "---------------------\n"
        for k, v in bracket.items():
            answer += k + " - " + v + "\n"
    answer += "---------------------"
    return answer


async def get_most_used_statistics_brackets(telegram_id: int) \
        -> typing.Tuple[typing.Dict[str, str], typing.Dict[str, str]] | None:
    """
    Get read-ready detailed most used statistics about user.

    :param telegram_id: User telegram id
    :return: Tuple of Dictionaries with statistical data pairs or None if user doesn't pass any quiz
    """

    statistics = await get_user_statistics(telegram_id)
    mu = statistics.most_used_wpos_and_qac
    if not mu:
        return None
    wpos, qac = dict(), dict()
    rus, eng = list(
        constants.PARTS_OF_SPEECH_TRANSLATIONS.keys()
    ), list(
        constants.PARTS_OF_SPEECH_TRANSLATIONS.values()
    )
    logger.debug(f"Starts get most used statistics for: {telegram_id}")
    for setting, statistics_setting in mu.items():
        percents = round((statistics_setting * 100) / statistics.total_quizzes, 2)
        logger.debug(f"Setting: {setting} has: {percents}% of usage.")
        if isinstance(setting, int):
            qac[f"{setting} вариантов ответа"] = f"{statistics_setting} раз, {percents}%"
        elif isinstance(setting, str) or setting is None:
            wpos[f"{rus[eng.index(setting)]}"] = f"{statistics_setting} раз, {percents}%"
    return wpos, qac


async def get_random_quiz(telegram_id: int) -> typing.Tuple[str, typing.List, int, int]:
    """
    Create a random quiz for the user according to their settings.

    :param telegram_id: User telegram id
    :return: Tuple of English version of the generated word,
    List of answer choices, index of correct answer, quiz validity time.
    """

    settings = await get_user_settings(telegram_id)
    english, russian = api.get_random_word(settings.words_part_of_speech)
    logger.debug(f"Success get random word: {english}, translation: {russian}.")
    options = [russian]
    options.extend(
        [api.get_random_word(settings.words_part_of_speech)[1] for _ in range(settings.quiz_answers_count - 1)]
    )
    logger.debug(f"Success extend answers list: {options}.")
    random.shuffle(options)
    logger.debug(f"Success shuffle options list: {options}.")
    correct_option_id = options.index(russian)
    open_period = constants.QUIZ_ANSWER_TIME_BY_USER_ANSWERS_COUNT[settings.quiz_answers_count]
    logger.debug(f"Success get open period for quiz: {open_period}.")

    return english, options, correct_option_id, open_period


async def quiz_answer_check(
        telegram_id: int,
        poll_id: int,
        answer_id: typing.Optional[int] = None
) -> bool:
    """
    Checking the answer to the quiz.

    :param telegram_id: User telegram id
    :param poll_id: Quiz id
    :param answer_id: Optional. Identifier of the response received from the user
    :return: Flag is user statistics updated
    """

    correct_option_id = await redis.get(f"{poll_id}")
    if not correct_option_id:
        return False
    await redis.delete(f"{poll_id}")
    correct_option_id = int(correct_option_id.decode("utf-8"))
    logger.debug(f"Success get correct option id from redis: {correct_option_id} for: {poll_id} poll.")
    is_correct = correct_option_id == answer_id
    logger.debug(f"Quiz: {poll_id} completed: {telegram_id} as: {is_correct}.")
    await update_correct_or_incorrect_answers(
        telegram_id,
        is_correct
    )
    logger.debug(f"Success update STATISTICS for: {telegram_id} user.")
    await update_most_used_wpos_and_qac_statistics(telegram_id)
    return True


async def check_quiz_completion(telegram_id: int, poll: Poll) -> None:
    """
    Verifying that the quiz has been taken during its open period.

    :param telegram_id: User telegram id
    :param poll: Verification quiz
    """

    await asyncio.sleep(poll.open_period)
    logger.debug(f"Checks quiz: {poll.id} completion...")
    flag = await quiz_answer_check(telegram_id, int(poll.id), -1)
    logger.debug(f"Quiz: {poll.id} passed " + ("NOT " if flag else "") + "IN-time!")
