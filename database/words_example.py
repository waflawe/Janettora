import sys
from pathlib import Path
from importlib import import_module

from sqlalchemy import select

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

database = import_module("database", "database")
models = import_module("models", "database")


def main() -> None:
    all_words = select(models.Word)
    with database.session_factorylite() as sessionlite:
        with database.session_factory() as sessionmain:
            all_words = sessionlite.execute(all_words).all()
            for word in all_words:
                w = word[0]
                word = models.Word(english=w.english, russian=w.russian, part_of_speech=w.part_of_speech)
                sessionmain.add(word)
            sessionmain.commit()


if __name__ == "__main__":
    models.Word.__table__.drop(database.engine, checkfirst=True)
    models.Word.metadata.create_all(database.engine)

    main()
