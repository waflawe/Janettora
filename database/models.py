import typing
from enum import StrEnum

from sqlalchemy import Column, Enum, MetaData
from sqlalchemy.orm import Mapped, mapped_column

from database import Model, engine


class WordPartsOfSpeech(StrEnum):
    NOUN = "noun"
    ADJECTIVE = "adjective"
    VERB = "verb"
    PHRASAL_VERB = "phrasal_verb"
    IRREGULAR_VERB = "irregular_verb"
    ADVERB = "adverb"
    IDIOM = "idiom"
    PHRASE = "phrase"

    @classmethod
    def get_valid_values(cls) -> typing.Tuple:
        return tuple(x.value for x in cls)


class Word(Model):
    __tablename__ = "words"
    metadata = MetaData()

    id: Mapped[int] = mapped_column(primary_key=True)
    english: Mapped[str]
    russian: Mapped[str]
    part_of_speech: Mapped[str] = Column(Enum(WordPartsOfSpeech))


class UserStatistics(Model):
    __tablename__ = "statistics"
    metadata = MetaData()

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    total_quizzes: Mapped[int]
    total_correct: Mapped[int]
    total_incorrect: Mapped[int]


def create_word_model() -> None:
    Word.metadata.create_all(engine)
    UserStatistics.metadata.create_all(engine)


def destroy_word_model() -> None:
    Word.metadata.drop_all(engine)
