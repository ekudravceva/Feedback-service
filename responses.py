"""Функции для работы с ответами администратора на сообщения."""

from datetime import datetime
from typing import Iterator


def is_message_answered(responses: list[dict], message_id: int) -> bool:
    """Проверить, есть ли уже ответ на сообщение с данным идентификатором."""
    return any(response["message_id"] == message_id for response in responses)


def generate_response_id(responses: list[dict]) -> int:
    """Сгенерировать новый идентификатор ответа."""
    if not responses:
        return 1
    return max(response["id"] for response in responses) + 1


def create_response(responses: list[dict], message_id: int, text: str) -> dict:
    """Создать новый ответ на сообщение.

    Вызывает ValueError, если ответ на это сообщение уже существует.
    """
    if is_message_answered(responses, message_id):
        raise ValueError("Ответ на это сообщение уже существует")

    response = {
        "id": generate_response_id(responses),
        "message_id": message_id,
        "text": text,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    responses.append(response)
    return response


def cancel_response(responses: list[dict], response_id: int) -> bool:
    """Удалить ответ по идентификатору, вернуть True при успехе."""
    for index, response in enumerate(responses):
        if response["id"] == response_id:
            del responses[index]
            return True
    return False


def get_responses_for_message(responses: list[dict], message_id: int) -> list[dict]:
    """Вернуть все ответы, относящиеся к заданному сообщению."""
    return [response for response in responses if response["message_id"] == message_id]


def iter_unanswered_messages(
    messages: list[dict],
    responses: list[dict],
) -> Iterator[dict]:
    """Вернуть генератор сообщений, на которые еще не дан ответ."""
    answered_ids = {response["message_id"] for response in responses}
    for message in messages:
        if message["id"] not in answered_ids:
            yield message
