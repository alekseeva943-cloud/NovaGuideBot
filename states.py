# =========================================
# FILE: states.py
# PATH: /NovaGuideBot/states.py
#
# ОТВЕЧАЕТ ЗА:
# - FSM состояния пользователя
# - onboarding нового пользователя
# - изменение анкеты
#
# FSM (Finite State Machine) —
# это система состояний пользователя.
#
# Пример:
# бот спросил имя →
# пользователь находится в состоянии
# waiting_for_name
# =========================================

from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup


# =========================================
# СОСТОЯНИЯ ПЕРВИЧНОЙ РЕГИСТРАЦИИ
# =========================================

class RegistrationStates(StatesGroup):

    # Пользователь вводит свое имя
    waiting_for_name = State()

    # Пользователь выбирает язык
    waiting_for_language = State()

    # Пользователь выбирает стиль общения
    waiting_for_style = State()


# =========================================
# СОСТОЯНИЯ РЕДАКТИРОВАНИЯ АНКЕТЫ
# =========================================

class EditProfileStates(StatesGroup):

    # Изменение имени
    editing_name = State()

    # Изменение языка
    editing_language = State()

    # Изменение стиля общения
    editing_style = State()