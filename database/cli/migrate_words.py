import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

database = import_module("database", "database")
models = import_module("models", "database")
config = import_module("config").config
exceptions = import_module("exceptions")
collect_words = import_module("collect_words", "database.cli")


def get_engine() -> Engine | None:
    """
    Get engine from config.

    :return: sqlalchemy.engine.Engine object or None if database engine configured incorrect in the config
    """

    return create_engine(
        f"sqlite:///{config.SQLITE_WORDS_DB_TO_DOCKER_NAME}",
        echo=config.DEBUG,
        pool_size=10
    )


engine = get_engine()
session_factory_words = sessionmaker(engine)

if __name__ == "__main__":
    models.Word.__table__.drop(database.engine, checkfirst=True)
    models.Word.__table__.create(database.engine)

    try:
        collect_words.collect_words(session_factory_words, database.session_factory)
    except OperationalError:
        raise exceptions.JanettoraConfigError("SQLITE_WORDS_DB_TO_DOCKER_NAME")
