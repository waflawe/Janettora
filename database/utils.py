from database import session_factory
from database.models import Word, WordPartsOfSpeech


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
