import os

from dotenv import load_dotenv

load_dotenv()

DB_NAME: str = os.getenv("DB_NAME")
DB_USER: str = os.getenv("DB_USER")
DB_PASSWORD: str = os.getenv("DB_PASSWORD")
DB_HOST: str = os.getenv("DB_HOST")
DB_PORT: int = int(os.getenv("DB_PORT"))

SQLALCHEMY_DEBUG_MODE: int = int(os.getenv("SQLALCHEMY_DEBUG_MODE"))

TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN")
DEBUG: int = int(os.getenv("DEBUG"))
REDIS_HOST: str = os.getenv("REDIS_HOST")
REDIS_PORT: int = int(os.getenv("REDIS_PORT"))
REDIS_DB_NUMBER: int = int(os.getenv("REDIS_DB_NUMBER"))
