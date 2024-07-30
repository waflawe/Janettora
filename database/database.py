import sys
import typing
from importlib import import_module
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config").config


def get_engine(namespace: typing.Optional[str] = None) -> Engine:
    if namespace: namespace += "_"   # noqa
    else: namespace = ""   # noqa

    return create_engine(
        URL.create(
            drivername="postgresql+psycopg",
            username=getattr(config, namespace + "DB_USER"),
            password=getattr(config, namespace + "DB_PASSWORD"),
            host=getattr(config, namespace + "DB_HOST"),
            port=getattr(config, namespace + "DB_PORT"),
            database=getattr(config, namespace + "DB_NAME")
        ),
        echo=config.DEBUG,
        pool_size=10
    )


engine = get_engine()

session_factory = sessionmaker(engine)


class Model(DeclarativeBase):
    pass
