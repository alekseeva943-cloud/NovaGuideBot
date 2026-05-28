# =========================================
# FILE: keyboards.py
# PATH: /NovaGuideBot/keyboards.py
#
# ОТВЕЧАЕТ ЗА:
# - Reply клавиатуры
# - Inline клавиатуры
# - onboarding кнопки
# =========================================

from telegram import (
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)


# =========================================
# ГЛАВНОЕ МЕНЮ
# =========================================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        ["👤 Моя анкета"]
    ],
    resize_keyboard=True
)


# =========================================
# КНОПКИ ВЫБОРА ИМЕНИ
# =========================================

name_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="✅ Оставить",
            callback_data="keep_name"
        ),

        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data="change_name"
        )
    ]
])


# =========================================
# КНОПКИ ВЫБОРА ЯЗЫКА
# =========================================

language_keyboard = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="✅ Оставить",
            callback_data="keep_language"
        ),

        InlineKeyboardButton(
            text="✏️ Изменить",
            callback_data="change_language"
        )
    ]
])