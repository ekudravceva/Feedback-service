"""Тесты класса Response и функций работы с коллекцией ответов."""

import pytest

from models import User
from models.messages import Message
from models.responses import cancel_response, create_response, is_message_answered


def make_message() -> Message:
    """Создать тестовое сообщение, на которое можно ответить."""
    author = User(1, "Тестовый пользователь", "test@example.com", "user")
    return Message(1, author, "Общее", "Проблема с входом в систему")


def test_create_response():
    message = make_message()
    responses = []
    response = create_response(responses, message, "Ответ администратора на обращение")
    assert len(responses) == 1
    assert response.message is message
    assert message.status == "закрыта"


def test_duplicate_response_forbidden():
    message = make_message()
    responses = []
    create_response(responses, message, "Первый ответ на сообщение")
    with pytest.raises(ValueError):
        create_response(responses, message, "Повторный ответ")


def test_is_message_answered():
    message = make_message()
    responses = []
    assert not is_message_answered(responses, message.id)
    create_response(responses, message, "Ответ администратора на обращение")
    assert is_message_answered(responses, message.id)


def test_cancel_response():
    message = make_message()
    responses = []
    create_response(responses, message, "Ответ администратора на обращение")
    assert cancel_response(responses, 1)
    assert len(responses) == 0
