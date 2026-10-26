"""Подключение к базе данных SQLite сервиса обратной связи."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = str(BASE_DIR / "data" / "feedback.sqlite")
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def _lower_u(value):
    """Привести строку к нижнему регистру (в том числе для кириллицы).

    Встроенные lower() и LIKE в SQLite понимают регистр только для латиницы,
    поэтому для регистронезависимого поиска по русскому тексту в соединение
    добавляется собственная SQL-функция lower_u().
    """
    return value.lower() if isinstance(value, str) else value


def get_connection(create=False):
    """Создать соединение с базой данных и настроить его.

    Если файл базы данных не найден и create=False, вызывается
    FileNotFoundError: так приложение не создаёт пустую базу «по ошибке».
    """
    if not create and not Path(DB_PATH).exists():
        raise FileNotFoundError(
            f"База данных {DB_PATH} не найдена. Создайте её командой: "
            "python -m db.import_json"
        )
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("lower_u", 1, _lower_u, deterministic=True)
    return conn


def create_schema(conn):
    """Создать таблицы по файлу sql/schema.sql (повторный запуск безопасен)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
