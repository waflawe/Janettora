from sqlalchemy import URL, create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, SQLALCHEMY_DEBUG_MODE

engine = create_engine(
    URL.create(
        drivername="postgresql+psycopg",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    ),
    echo=SQLALCHEMY_DEBUG_MODE,
    pool_size=1
)

session_factory = sessionmaker(engine)


class Model(DeclarativeBase):
    pass
