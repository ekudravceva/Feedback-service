"""Тесты слоя базы данных SQLite: схема, импорт из JSON и файл запросов."""

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from db import database, import_json

ROOT = Path(__file__).resolve().parent.parent
QUERIES_FILE = ROOT / "sql" / "queries.sql"


@pytest.fixture
def conn(tmp_path):
    """Пустая база по sql/schema.sql."""
    path = tmp_path / "test.sqlite"
    with patch.object(database, "DB_PATH", str(path)):
        connection = database.get_connection(create=True)
        database.create_schema(connection)
        yield connection
        connection.close()


@pytest.fixture
def filled(conn):
    """База, заполненная данными тем же кодом, что и импорт из JSON."""
    import_json.import_users(conn)
    import_json.import_messages(conn)
    import_json.import_responses(conn)
    conn.commit()
    return conn


def table_names(conn):
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    return {row[0] for row in rows}


def test_schema_creates_tables(conn):
    assert {"users", "messages", "responses"} <= table_names(conn)


def test_schema_can_be_applied_twice(conn):
    database.create_schema(conn)
    assert {"users", "messages", "responses"} <= table_names(conn)


def test_foreign_keys_are_declared(conn):
    messages_fk = conn.execute("PRAGMA foreign_key_list(messages)").fetchall()
    responses_fk = conn.execute("PRAGMA foreign_key_list(responses)").fetchall()
    assert [row[2] for row in messages_fk] == ["users"]
    assert [row[2] for row in responses_fk] == ["messages"]


def test_foreign_keys_are_enforced(conn):
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO messages (id, user_id, category, text, created_at) "
            "VALUES (1, 999, 'Общее', 'Текст', '2026-01-01 10:00')"
        )


def test_status_check_constraint(conn):
    conn.execute(
        "INSERT INTO users (id, name, email) VALUES (1, 'A', 'a@a.ru')"
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO messages (id, user_id, category, text, status, "
            "created_at) VALUES (1, 1, 'Общее', 'Текст', 'неизвестно', "
            "'2026-01-01 10:00')"
        )


def test_one_response_per_message(filled):
    with pytest.raises(sqlite3.IntegrityError):
        filled.execute(
            "INSERT INTO responses (id, message_id, text, created_at) "
            "VALUES (99, 2, 'Второй ответ', '2026-01-01 10:00')"
        )


def test_import_matches_json_files(filled):
    for table, filename in (
        ("users", import_json.USERS_FILE),
        ("messages", import_json.MESSAGES_FILE),
        ("responses", import_json.RESPONSES_FILE),
    ):
        expected = len(import_json.load_json(filename))
        actual = filled.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        assert actual == expected, table


def test_import_refuses_non_empty_database(tmp_path, capsys):
    path = tmp_path / "test.sqlite"
    with patch.object(database, "DB_PATH", str(path)):
        assert import_json.main([]) == 0
        assert import_json.main([]) == 1
        assert "уже есть данные" in capsys.readouterr().out
        assert import_json.main(["--reset"]) == 0


def test_missing_database_is_reported(tmp_path):
    with patch.object(database, "DB_PATH", str(tmp_path / "none.sqlite")):
        with pytest.raises(FileNotFoundError):
            database.get_connection()


def test_lower_u_function_handles_cyrillic(conn):
    assert conn.execute("SELECT lower_u('ПРИВЕТ')").fetchone()[0] == "привет"
    assert conn.execute("SELECT lower_u(NULL)").fetchone()[0] is None


def split_queries(text):
    """Разделить файл запросов на отдельные команды (без комментариев)."""
    lines = [
        line for line in text.splitlines()
        if not line.strip().startswith("--")
    ]
    statements = "\n".join(lines).split(";")
    return [item.strip() for item in statements if item.strip()]


def test_queries_file_has_enough_queries_of_each_kind():
    queries = split_queries(QUERIES_FILE.read_text(encoding="utf-8"))
    assert len(queries) >= 10
    upper = [" ".join(query.upper().split()) for query in queries]
    assert sum(" WHERE " in q for q in upper) >= 2
    assert sum(" JOIN " in q for q in upper) >= 2
    assert sum("COUNT(" in q for q in upper) >= 2
    assert sum(" GROUP BY " in q for q in upper) >= 2
    assert sum(" HAVING " in q for q in upper) >= 1


def test_all_queries_run_on_real_schema(filled):
    queries = split_queries(QUERIES_FILE.read_text(encoding="utf-8"))
    for query in queries:
        filled.execute(query).fetchall()


def test_queries_use_parameters_not_string_building():
    from feedback import views as feedback_views
    from responses import views as responses_views

    for module in (feedback_views, responses_views):
        source = Path(module.__file__).read_text(encoding="utf-8")
        assert 'f"""' not in source
        assert ".format(" not in source
