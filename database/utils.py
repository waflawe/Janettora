import random
import sys
import typing
from importlib import import_module
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError

from database import engine, session_factory
from database.models import Model, UserSettings, UserStatistics, Word, WordPartsOfSpeech

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config")
constants = import_module("constants", "bot")

########################################
# PRIVATE UTILITIES FOR CODE REDUCTION #
########################################


def _create_object(model: typing.Type[Model], **kwargs) -> Model:
    """
    Creating an object in the database.

    :param model: A reference to the model whose object will be created
    :param kwargs: Parameters passed to the model when creating the object
    :return: Created object
    """

    object_ = model(**kwargs)
    with session_factory() as session:
        session.add(object_)
        session.commit()
    return object_


def _get_user_related_model_object(model: typing.Type[Model], telegram_id: int) -> Model:
    """
    Retrieve the model object associated with the user.

    :param model: Link on the model
    :param telegram_id: User telegram id
    :return: Selected object
    """

    query = select(model).where(model.telegram_id == telegram_id)
    with session_factory() as session:
        result = session.execute(query).all()[0][0]
        return result


def _update_user_related_model_object(model: typing.Type[Model], **kwargs) -> None:
    """
    Update user related model object by kwargs.

    :param kwargs: User telegram id and the values that need to be updated.
    """

    with session_factory() as session:
        session.execute(
            update(model),
            [
                kwargs
            ]
        )
        session.commit()


####################
# PUBLIC UTILITIES #
####################


def create_word(english: str, russian: str, part_of_speech: WordPartsOfSpeech) -> None:
    """
    Create word in model Word.

    :param english: English-translated word
    :param russian: Russian-translated word
    :param part_of_speech: Part of speech of english-translated word from database.models.WordPartsOfSpeech enum
    """

    _create_object(Word, english=english, russian=russian, part_of_speech=part_of_speech)


def register_user_in_databases(telegram_id: int) -> None:
    """
    Register user in the UserSettings and UserStatistics models.

    :param telegram_id: User telegram id
    """

    try:
        _create_object(UserSettings, telegram_id=telegram_id)
        _create_object(UserStatistics, telegram_id=telegram_id)
    except IntegrityError:
        pass


def get_random_word(part_of_speech: typing.Optional[str] = None) -> typing.Tuple[str, str]:
    """
    Get random word from Word model.

    :param part_of_speech: Optional parameter to generate a random word of a certain part of speech
    :return: Tuple from the English and Russian translations of the word
    """

    words = select(Word)
    if part_of_speech:
        words = words.where(Word.part_of_speech == part_of_speech)
    with session_factory() as session:
        result = session.execute(words).all()
        random_word = random.choice(result)[0]
        return random_word.english, random_word.russian


def get_user_settings(telegram_id: int) -> UserSettings:
    """
    Get UserSettings object by user telegram id.

    :param telegram_id: User telegram id
    :return: UserSettings object with user settings
    """

    return _get_user_related_model_object(UserSettings, telegram_id)


def get_user_statistics(telegram_id: int) -> UserStatistics:
    """
    Get UserStatistics object by user telegram id.

    :param telegram_id: User telegram id
    :return: UserStatistics object with user statistics
    """

    return _get_user_related_model_object(UserStatistics, telegram_id)


def change_quiz_answers_count(telegram_id: int) -> None:
    """
    Change quiz_answers_count user setting.

    :param telegram_id: User telegram id
    """

    settings = get_user_settings(telegram_id)
    quiz_answers_count = settings.quiz_answers_count
    if quiz_answers_count+1 in UserSettings.QUIZ_ANSWERS_COUNT_RANGE:
        quiz_answers_count += 1
    else:
        quiz_answers_count = UserSettings.QUIZ_ANSWERS_COUNT_RANGE.start
    _update_user_related_model_object(
        UserSettings,
        telegram_id=telegram_id,
        quiz_answers_count=quiz_answers_count
    )


def change_words_part_of_speech(telegram_id: int) -> None:
    """
    Change words_part_of_speech user setting.

    :param telegram_id: User telegram id
    """

    settings = get_user_settings(telegram_id)
    words_part_of_speech = settings.words_part_of_speech
    pos_english = list(constants.PARTS_OF_SPEECH_TRANSLATIONS.values())
    try:
        words_part_of_speech = pos_english[pos_english.index(words_part_of_speech)+1]
    except IndexError:
        words_part_of_speech = pos_english[0]
    _update_user_related_model_object(
        UserSettings,
        telegram_id=telegram_id,
        words_part_of_speech=words_part_of_speech
    )


def update_correct_or_incorrect_answers(telegram_id: int, is_correct: bool) -> None:
    """
    Update the total_correct or total_incorrect field in the user's statistics.

    :param telegram_id: User telegram id
    :param is_correct: Flag to indicate the field to be updated
    """

    statistics = _get_user_related_model_object(UserStatistics, telegram_id)
    kwargs = {"telegram_id": telegram_id, "total_quizzes": statistics.total_quizzes+1}
    attr = "total_correct" if is_correct else "total_incorrect"
    kwargs[attr] = getattr(statistics, attr) + 1
    _update_user_related_model_object(UserStatistics, **kwargs)


###############################
# MODELS CREATION AND DESTROY #
###############################


def create_word_model() -> None:
    Word.metadata.create_all(engine)


def destroy_word_model() -> None:
    Word.metadata.drop_all(engine)


def recreate_settings_and_statistics_model() -> None:
    UserSettings.metadata.create_all(engine)
    UserStatistics.metadata.create_all(engine)
