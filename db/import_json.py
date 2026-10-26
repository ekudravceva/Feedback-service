"""Однократный перенос данных из JSON-файлов в базу данных SQLite.

Запуск из корня проекта:
    python -m db.import_json            # перенос в пустую базу
    python -m db.import_json --reset    # очистить таблицы и перенести заново
"""

import json
import sys
from pathlib import Path

from db.database import create_schema, get_connection

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
USERS_FILE = DATA_DIR / "users.json"
MESSAGES_FILE = DATA_DIR / "messages.json"
RESPONSES_FILE = DATA_DIR / "responses.json"


def load_json(filename):
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def import_users(conn):
    users = load_json(USERS_FILE)
    conn.executemany(
        """
        INSERT INTO users (id, name, email, role)
        VALUES (?, ?, ?, ?)
        """,
        [
            (user["id"], user["name"], user["email"], user["role"])
            for user in users
        ],
    )
    return len(users)


def import_messages(conn):
    messages = load_json(MESSAGES_FILE)
    conn.executemany(
        """
        INSERT INTO messages (
            id,
            user_id,
            category,
            text,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                message["id"],
                message["user_id"],
                message["category"],
                message["text"],
                message["status"],
                message["created_at"],
            )
            for message in messages
        ],
    )
    return len(messages)


def import_responses(conn):
    responses = load_json(RESPONSES_FILE)
    conn.executemany(
        """
        INSERT INTO responses (id, message_id, text, created_at)
        VALUES (?, ?, ?, ?)
        """,
        [
            (
                response["id"],
                response["message_id"],
                response["text"],
                response["created_at"],
            )
            for response in responses
        ],
    )
    return len(responses)


def clear_tables(conn):
    """Удалить данные в порядке, обратном импорту (из-за внешних ключей)."""
    conn.execute("DELETE FROM responses")
    conn.execute("DELETE FROM messages")
    conn.execute("DELETE FROM users")


def is_empty(conn):
    return all(
        conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] == 0
        for table in ("users", "messages", "responses")
    )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    reset = "--reset" in argv

    conn = get_connection(create=True)
    try:
        create_schema(conn)
        if reset:
            clear_tables(conn)
        elif not is_empty(conn):
            print(
                "В базе уже есть данные: перенос не выполнен. "
                "Для повторного импорта запустите с ключом --reset."
            )
            return 1
        # Порядок важен: сначала таблицы, на которые ссылаются внешние ключи.
        counts = (
            import_users(conn),
            import_messages(conn),
            import_responses(conn),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(
        "Импорт выполнен: пользователей — {}, сообщений — {}, "
        "ответов — {}.".format(*counts)
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
