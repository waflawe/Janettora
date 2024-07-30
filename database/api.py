import random
import sys
import typing
from importlib import import_module
from pathlib import Path

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import aliased

from database import engine, session_factory
from database.models import Model, UserSettings, UserStatistics, Word, WordPartsOfSpeech

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config").config

if "bot/" in sys.argv[0]:
    constants = import_module("constants", "bot")
elif "parser/" in sys.argv[0]:
    constants = import_module("bot.constants")

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

    query = select(model).where(model.telegram_id == telegram_id)   # noqa
    with session_factory() as session:
        result = session.execute(query).scalars().all()[0]
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


def register_user_in_databases(telegram_id: int) -> bool:
    """
    Register user in the UserSettings and UserStatistics models.

    :param telegram_id: User telegram id
    :return: Flag is user registered
    """

    try:
        _create_object(UserSettings, telegram_id=telegram_id)
        _create_object(UserStatistics, telegram_id=telegram_id)
        return True
    except IntegrityError:
        return False


def get_random_word(part_of_speech: typing.Optional[str] = None) -> typing.Tuple[str, str]:
    """
    Get random word from Word model.

    :param part_of_speech: Optional parameter to generate a random word of a certain part of speech
    :return: Tuple from the English and Russian translations of the word
    """

    w = aliased(Word)
    words = select(w)
    if part_of_speech:
        words = words.where(w.part_of_speech == part_of_speech)
    with session_factory() as session:
        result = session.execute(words).scalars().all()
        random_word = random.choice(result)
        return random_word.english, random_word.russian


def get_user_settings(telegram_id: int) -> UserSettings:
    """
    Get UserSettings object by user telegram id.

    :param telegram_id: User telegram id
    :return: UserSettings object with user settings
    """

    return _get_user_related_model_object(UserSettings, telegram_id)   # noqa


def get_user_statistics(telegram_id: int) -> UserStatistics:
    """
    Get UserStatistics object by user telegram id.

    :param telegram_id: User telegram id
    :return: UserStatistics object with user statistics
    """

    return _get_user_related_model_object(UserStatistics, telegram_id)   # noqa


def update_user_settings(telegram_id: int, **kwargs) -> None:
    """
    Update user settings.

    :param telegram_id: User telegram id
    :param kwargs: Fields and his values to update
    """

    _update_user_related_model_object(
        UserSettings,
        telegram_id=telegram_id,
        **kwargs
    )


def update_user_statistics(telegram_id: int, **kwargs) -> None:
    """
    Update user statistics.

    :param telegram_id: User telegram id
    :param kwargs: Fields and his values to update
    """

    _update_user_related_model_object(
        UserStatistics,
        telegram_id=telegram_id,
        **kwargs
    )


def get_quiz_answers_count_range() -> range:
    return UserSettings.QUIZ_ANSWERS_COUNT_RANGE


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
