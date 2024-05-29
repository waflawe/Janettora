from database import session_factory
from database.models import Word, WordPartsOfSpeech
from sqlalchemy import select
import typing
from importlib import import_module
from pathlib import Path
import sys
import random

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

keyboards = import_module("keyboards", "bot")


def create_word(english: str, russian: str, part_of_speech: WordPartsOfSpeech) -> None:
    """
    Create word in model Word.

    :param english: English-translated word
    :param russian: Russian-translated word
    :param part_of_speech: Part of speech of english-translated word from database.models.WordPartsOfSpeech enum
    """

    word = Word(english=english, russian=russian, part_of_speech=part_of_speech)
    with session_factory() as session:
        session.add(word)
        session.commit()


def get_random_word(part_of_speech: typing.Optional[str] = None) -> typing.Tuple[str, str]:
    """
    Get random word from Word model.

    :param part_of_speech: Optional parameter to generate a random word of a certain part of speech
    :return: Tuple from the English and Russian translations of the word
    """

    words = select(Word)
    if part_of_speech:
        words = words.where(Word.part_of_speech == keyboards.PARTS_OF_SPEECH_TRANSLATIONS[part_of_speech])
    with session_factory() as session:
        result = session.execute(words).all()
        random_word = random.choice(result)[0]
        return random_word.english, random_word.russian
