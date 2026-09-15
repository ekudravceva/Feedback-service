"""Тесты функций работы с сообщениями."""

import pytest

from messages import (
    add_message,
    check_message_validity,
    filter_messages_by_status,
    find_messages,
)


def test_add_message():
    messages = []
    add_message(messages, 1, "Общее", "Тестовое сообщение для проверки")
    assert len(messages) == 1


def test_add_message_invalid_raises():
    messages = []
    with pytest.raises(ValueError):
        add_message(messages, 1, "Общее", "коротко")


def test_find_messages():
    messages = []
    add_message(messages, 1, "Общее", "Проблема с входом в систему")
    assert find_messages(messages, "проблема")


def test_filter_messages_by_status():
    messages = []
    add_message(messages, 1, "Общее", "Проблема с входом в систему")
    assert len(filter_messages_by_status(messages, "новая")) == 1


def test_check_message_validity_bad_category():
    is_valid, _ = check_message_validity("Нормальный текст сообщения", "Несуществующая")
    assert not is_valid
