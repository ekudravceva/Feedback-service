"""Вспомогательные средства для тестов: временная база данных SQLite."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.test import TestCase

from db import database

USERS = [
    (1, "Анна Иванова", "anna@example.com", "user"),
    (2, "Администратор", "admin@example.com", "admin"),
    (3, "Сергей Сергеев", "sergeev@mail.com", "user"),
]

MESSAGES = [
    (1, 1, "Техническая поддержка",
     "Не могу войти в личный кабинет, пишет ошибка 504", "новая",
     "2026-09-14 12:00"),
    (2, 3, "Жалоба", "Не могу авторизоваться", "закрыта",
     "2026-09-15 18:45"),
    (3, 1, "Общее", "<script>alert(1)</script> Вопрос по тарифам", "в обработке",
     "2026-10-19 20:22"),
]

RESPONSES = [
    (1, 2, "Починим", "2026-09-15 18:46"),
]


def create_test_database(path):
    """Создать базу по sql/schema.sql и заполнить тестовыми данными."""
    with patch.object(database, "DB_PATH", str(path)):
        conn = database.get_connection(create=True)
        try:
            database.create_schema(conn)
            conn.executemany("INSERT INTO users VALUES (?, ?, ?, ?)", USERS)
            conn.executemany(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?)", MESSAGES
            )
            conn.executemany(
                "INSERT INTO responses VALUES (?, ?, ?, ?)", RESPONSES
            )
            conn.commit()
        finally:
            conn.close()


class TempDatabaseTestCase(TestCase):
    """Базовый класс: каждый тест работает с отдельной временной базой."""

    def setUp(self):
        super().setUp()
        tmp_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        self.db_path = Path(tmp_dir) / "test.sqlite"
        create_test_database(self.db_path)
        patcher = patch.object(database, "DB_PATH", str(self.db_path))
        patcher.start()
        self.addCleanup(patcher.stop)
