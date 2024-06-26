import sys
from importlib import import_module
from pathlib import Path

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

config = import_module("config").config

engine = create_engine(
    URL.create(
        drivername="postgresql+psycopg",
        username=config.DB_USER,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT,
        database=config.DB_NAME
    ),
    echo=config.DEBUG,
    pool_size=10
)

session_factory = sessionmaker(engine)


class Model(DeclarativeBase):
    pass
