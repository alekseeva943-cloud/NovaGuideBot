# =========================================
# FILE: database.py
# PATH: /NovaGuideBot/database.py
#
# ОТВЕЧАЕТ ЗА:
# - подключение к SQLite
# - создание базы данных
# - сохранение профиля пользователя
# - получение данных пользователя
# - обновление анкеты
# =========================================

import sqlite3
from typing import Optional


# =========================================
# Название файла базы данных
# =========================================

DB_NAME = "users.db"


# =========================================
# Создание таблицы users
#
# Вызывается один раз при старте бота.
# =========================================

def init_db() -> None:
    """
    Создает таблицу users, если она еще не существует.
    """

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            language TEXT NOT NULL,
            style TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# =========================================
# Получение пользователя
#
# Возвращает:
# - dict с данными пользователя
# - либо None, если пользователя нет
# =========================================

def get_user(telegram_id: int) -> Optional[dict]:

    conn = sqlite3.connect(DB_NAME)

    # Позволяет обращаться к колонкам по имени
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT * FROM users
        WHERE telegram_id = ?
        """,
        (telegram_id,)
    )

    user = cursor.fetchone()

    conn.close()

    if user is None:
        return None

    return dict(user)


# =========================================
# Сохранение пользователя
#
# Используем UPSERT:
# - если пользователя нет → создаем
# - если есть → обновляем
# =========================================

def save_user(
    telegram_id: int,
    name: str,
    language: str,
    style: str
) -> None:

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (
            telegram_id,
            name,
            language,
            style
        )
        VALUES (?, ?, ?, ?)

        ON CONFLICT(telegram_id)
        DO UPDATE SET
            name = excluded.name,
            language = excluded.language,
            style = excluded.style
    """, (
        telegram_id,
        name,
        language,
        style
    ))

    conn.commit()
    conn.close()


# =========================================
# Обновление имени
# =========================================

def update_name(
    telegram_id: int,
    new_name: str
) -> None:

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET name = ?
        WHERE telegram_id = ?
    """, (
        new_name,
        telegram_id
    ))

    conn.commit()
    conn.close()


# =========================================
# Обновление языка
# =========================================

def update_language(
    telegram_id: int,
    new_language: str
) -> None:

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET language = ?
        WHERE telegram_id = ?
    """, (
        new_language,
        telegram_id
    ))

    conn.commit()
    conn.close()


# =========================================
# Обновление стиля общения
# =========================================

def update_style(
    telegram_id: int,
    new_style: str
) -> None:

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE users
        SET style = ?
        WHERE telegram_id = ?
    """, (
        new_style,
        telegram_id
    ))

    conn.commit()
    conn.close()