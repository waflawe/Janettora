import typing
from enum import StrEnum

from sqlalchemy import Column, Enum, MetaData, BigInteger
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

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    total_quizzes: Mapped[int] = mapped_column(default=0)
    total_correct: Mapped[int] = mapped_column(default=0)
    total_incorrect: Mapped[int] = mapped_column(default=0)


class UserSettings(Model):
    __tablename__ = "settings"
    metadata = MetaData()

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    words_part_of_speech: Mapped[str | None]
    quiz_answers_count: Mapped[int] = mapped_column(default=4)

    QUIZ_ANSWERS_COUNT_RANGE = range(4, 7)
