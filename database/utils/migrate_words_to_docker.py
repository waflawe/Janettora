import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy import select, create_engine
from sqlalchemy.orm import sessionmaker

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

database = import_module("database", "database")
models = import_module("models", "database")
config = import_module("config")

engine_lite = create_engine(
    f"sqlite:///{config.DATABASE_WITH_WORDS_TABLE_FOR_DOCKER_NAME}",
    echo=config.DEBUG,
    pool_size=1
)
session_factory_lite = sessionmaker(engine_lite)


def main() -> None:
    all_words = select(models.Word)
    with session_factory_lite() as session_lite:
        with database.session_factory() as session_main:
            all_words = session_lite.execute(all_words).all()
            for word in all_words:
                w = word[0]
                word = models.Word(english=w.english, russian=w.russian, part_of_speech=w.part_of_speech)
                session_main.add(word)
            session_main.commit()


if __name__ == "__main__":
    models.Word.__table__.drop(database.engine, checkfirst=True)
    models.Word.__table__.create(database.engine)

    main()
