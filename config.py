import os
import typing

from dotenv import load_dotenv


class JanettoraConfig(typing.NamedTuple):
    # RUNTIME
    TELEGRAM_BOT_TOKEN: str
    DEBUG: int

    # BOT USED DATABASE
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int

    # BOT USED REDIS
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB_NUMBER: int

    # DATABASE TO COLLECT WORDS FROM POSTGRESQL TO SQLITE
    COLLECT_WORDS_DB_NAME: str | None
    COLLECT_WORDS_DB_USER: str | None
    COLLECT_WORDS_DB_PASSWORD: str | None
    COLLECT_WORDS_DB_HOST: str | None
    COLLECT_WORDS_DB_PORT: int | None

    # DATABASE WITH WORDS TO DOCKER
    SQLITE_WORDS_DB_TO_DOCKER_NAME: str = "test_words.db"

    # CACHE
    CACHE_SETTINGS_VARIABLE_NAME: str = "settings"


load_dotenv()

config = JanettoraConfig(
    os.getenv("TELEGRAM_BOT_TOKEN"),
    int(os.getenv("DEBUG")),
    os.getenv("DB_NAME"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASSWORD"),
    os.getenv("DB_HOST"),
    int(os.getenv("DB_PORT")),
    os.getenv("REDIS_HOST"),
    int(os.getenv("REDIS_PORT")),
    int(os.getenv("REDIS_DB_NUMBER")),
    os.getenv("COLLECT_WORDS_DB_NAME", None),
    os.getenv("COLLECT_WORDS_DB_USER", None),
    os.getenv("COLLECT_WORDS_DB_PASSWORD", None),
    os.getenv("COLLECT_WORDS_DB_HOST", None),
    int(os.getenv("COLLECT_WORDS_DB_PORT", -1)),
    os.getenv("SQLITE_WORDS_DB_TO_DOCKER_NAME", "test_words.db"),
)
