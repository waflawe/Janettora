from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

PARTS_OF_SPEECH_TRANSLATIONS = {
    "Существительные": "NOUN",
    "Прилагательные": "ADJECTIVE",
    "Глаголы": "VERB",
    "Фразовые глаголы": "PHRASAL_VERB",
    "Неправильные глаголы": "IRREGULAR_VERB",
    "Наречия": "ADVERB",
    "Идиомы": "IDIOM",
    "Фразы": "PHRASE"
}

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Настройки"),
            KeyboardButton(text="Статистика")
        ],
        [
            KeyboardButton(text="Тренировка")
        ]
    ],
    resize_keyboard=True
)
