import sqlite3
from typing import Optional, Dict, Any

# Имя файла базы данных по умолчанию
DB_NAME = "users.db"


def init_db(db_path: str = DB_NAME) -> None:
    """
    Инициализирует базу данных SQLite и создает таблицу 'users'
    с полями: telegram_id, name, language, style.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            telegram_id INTEGER PRIMARY KEY,
            name TEXT,
            language TEXT,
            style TEXT
        )
    """)
    conn.commit()
    conn.close()


def get_user(telegram_id: int, db_path: str = DB_NAME) -> Optional[Dict[str, Any]]:
    """
    Получает данные профиля пользователя по его telegram_id.
    Если пользователь отсутствует в БД, возвращает None.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Доступ по названиям столбцов
    cursor = conn.cursor()
    cursor.execute(
        "SELECT telegram_id, name, language, style FROM users WHERE telegram_id = ?",
        (telegram_id,)
    )
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        return None
        
    return {
        "telegram_id": row["telegram_id"],
        "name": row["name"],
        "language": row["language"],
        "style": row["style"]
    }


def save_user(telegram_id: int, name: str, language: str, style: str, db_path: str = DB_NAME) -> None:
    """
    Сохраняет нового пользователя или перезаписывает существующего целиком.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (telegram_id, name, language, style)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(telegram_id) DO UPDATE SET
            name = excluded.name,
            language = excluded.language,
            style = excluded.style
    """, (telegram_id, name, language, style))
    conn.commit()
    conn.close()


def update_user_name(telegram_id: int, name: str, db_path: str = DB_NAME) -> None:
    """
    Обновляет исключительно имя пользователя.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET name = ? WHERE telegram_id = ?",
        (name, telegram_id)
    )
    conn.commit()
    conn.close()


def update_user_language(telegram_id: int, language: str, db_path: str = DB_NAME) -> None:
    """
    Обновляет исключительно предпочтительный язык общения.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET language = ? WHERE telegram_id = ?",
        (language, telegram_id)
    )
    conn.commit()
    conn.close()


def update_user_style(telegram_id: int, style: str, db_path: str = DB_NAME) -> None:
    """
    Обновляет исключительно предпочтительный стиль ведения диалога.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET style = ? WHERE telegram_id = ?",
        (style, telegram_id)
    )
    conn.commit()
    conn.close()
