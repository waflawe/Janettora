from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

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
