"""Тесты класса Message и функций работы с коллекцией сообщений."""

import pytest

from models import User
from models.messages import Message, add_message, filter_messages_by_status, find_messages


def make_author() -> User:
    """Создать тестового пользователя-автора сообщений."""
    return User(1, "Тестовый пользователь", "test@example.com", "user")


def test_message_creation():
    author = make_author()
    message = Message(1, author, "Общее", "Тестовое сообщение для проверки")
    assert message.id == 1
    assert message.author is author
    assert message.category == "Общее"
    assert message.status == "новая"


def test_message_str_contains_status_text():
    author = make_author()
    message = Message(1, author, "Общее", "Тестовое сообщение для проверки")
    assert "Новое сообщение" in str(message)


def test_message_validate_bad_category():
    is_valid, _ = Message.validate("Нормальный текст сообщения", "Несуществующая")
    assert not is_valid


def test_add_message():
    author = make_author()
    messages = []
    add_message(messages, author, "Общее", "Тестовое сообщение для проверки")
    assert len(messages) == 1


def test_add_message_invalid_raises():
    author = make_author()
    messages = []
    with pytest.raises(ValueError):
        add_message(messages, author, "Общее", "коротко")


def test_find_messages():
    author = make_author()
    messages = []
    add_message(messages, author, "Общее", "Проблема с входом в систему")
    assert find_messages(messages, "проблема")


def test_filter_messages_by_status():
    author = make_author()
    messages = []
    add_message(messages, author, "Общее", "Проблема с входом в систему")
    assert len(filter_messages_by_status(messages, "новая")) == 1
