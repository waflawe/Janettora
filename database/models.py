from sqlalchemy.orm import Mapped, mapped_column

from database import Model


class Word(Model):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)
    english: Mapped[str]
    russian: Mapped[str]
