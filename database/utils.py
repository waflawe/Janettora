from database import session_factory
from database.models import Word


def create_word(english: str, russian: str) -> None:
    """
    Create word in model Word.

    :param english: English-translated word
    :param russian: Russian-translated word
    """

    word = Word(english=english, russian=russian)
    with session_factory() as session:
        session.add(word)
        session.commit()
