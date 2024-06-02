import sys
from importlib import import_module
from pathlib import Path

from aiogram.types import InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

project_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(project_dir))

models = import_module("database.models")
constants = import_module("constants", "bot")

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Тренировка")
        ],
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Статистика")
        ]
    ],
    resize_keyboard=True
)


def settings_kb(settings: models.UserSettings) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    words_part_of_speech = list(
        constants.PARTS_OF_SPEECH_TRANSLATIONS.keys()
    )[list(
        constants.PARTS_OF_SPEECH_TRANSLATIONS.values()
    ).index(
        settings.words_part_of_speech
    )]
    builder.button(text=f"Кол-во вариантов ответа: {settings.quiz_answers_count}", callback_data="change_qac")
    builder.button(text=f"Часть речи слов: {words_part_of_speech}", callback_data="change_wpos")
    return builder.as_markup()
