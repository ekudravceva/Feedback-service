"""Тесты функций работы с ответами на сообщения."""

import pytest

from responses import cancel_response, create_response, is_message_answered


def test_create_response():
    responses = []
    create_response(responses, 1, "Ответ администратора на обращение")
    assert len(responses) == 1


def test_duplicate_response_forbidden():
    responses = []
    create_response(responses, 1, "Первый ответ на сообщение")
    with pytest.raises(ValueError):
        create_response(responses, 1, "Повторный ответ")


def test_is_message_answered():
    responses = []
    assert not is_message_answered(responses, 1)
    create_response(responses, 1, "Ответ администратора на обращение")
    assert is_message_answered(responses, 1)


def test_cancel_response():
    responses = []
    create_response(responses, 1, "Ответ администратора на обращение")
    assert cancel_response(responses, 1)
    assert len(responses) == 0
