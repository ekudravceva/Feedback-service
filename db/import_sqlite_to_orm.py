import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

import django
from django.db import transaction
from django.utils import timezone

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

SOURCE_DB = BASE_DIR / "data" / "feedback.sqlite"

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "feedback_service.settings")
django.setup()

# Модели импортируются только после инициализации Django.
from feedback.models import Message  # noqa: E402
from responses.models import Response  # noqa: E402
from users.models import User  # noqa: E402

DATE_FORMAT = "%Y-%m-%d %H:%M"


def parse_datetime(value):
    """Преобразовать строку из исходной базы в aware-datetime."""
    return timezone.make_aware(datetime.strptime(value, DATE_FORMAT))


def main():
    if not SOURCE_DB.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        users = connection.execute(
            "SELECT id, name, email, role FROM users ORDER BY id"
        ).fetchall()
        messages = connection.execute(
            "SELECT id, user_id, category, text, status, created_at "
            "FROM messages ORDER BY id"
        ).fetchall()
        responses = connection.execute(
            "SELECT id, message_id, text, created_at "
            "FROM responses ORDER BY id"
        ).fetchall()

    # Порядок важен: сначала независимые сущности, затем ссылающиеся на них.
    with transaction.atomic():
        for row in users:
            User.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "name": row["name"],
                    "email": row["email"],
                    "role": row["role"],
                },
            )
        for row in messages:
            Message.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "author_id": row["user_id"],
                    "category": row["category"],
                    "text": row["text"],
                    "status": row["status"],
                    "created_at": parse_datetime(row["created_at"]),
                },
            )
        for row in responses:
            Response.objects.update_or_create(
                pk=row["id"],
                defaults={
                    "message_id": row["message_id"],
                    "text": row["text"],
                    "created_at": parse_datetime(row["created_at"]),
                },
            )

    print("Перенос данных завершён.")
    print(f"Пользователей: {User.objects.count()} (в источнике {len(users)})")
    print(f"Сообщений: {Message.objects.count()} (в источнике {len(messages)})")
    print(f"Ответов: {Response.objects.count()} (в источнике {len(responses)})")


if __name__ == "__main__":
    main()
