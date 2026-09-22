"""Класс ответа и функции работы с коллекцией ответов на сообщения."""

from datetime import datetime
from typing import Iterator, List, Optional

from .messages import Message, find_message_by_id


class Response:
    """Ответ администратора на сообщение пользователя."""

    def __init__(
        self,
        response_id: int,
        message: Optional[Message],
        text: str,
        created_at: Optional[str] = None,
    ) -> None:
        """Создать объект ответа.

        Сохраняет идентификатор, сообщение (объект Message), к которому
        относится ответ, текст ответа и дату создания.
        """
        self.id = response_id
        self.message = message
        self.text = text
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M")

    def __str__(self) -> str:
        """Вернуть строковое представление ответа."""
        message_id = self.message.id if self.message else "—"
        return f"[{self.id}] на сообщение {message_id} ({self.created_at}): {self.text}"

    @classmethod
    def from_data(cls, data: dict, messages: List[Message]) -> "Response":
        """Создать ответ из набора данных, связав его с объектом Message."""
        message = find_message_by_id(messages, data["message_id"])
        return cls(data["id"], message, data["text"], data["created_at"])

    def to_data(self) -> dict:
        """Преобразовать ответ в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "message_id": self.message.id if self.message else None,
            "text": self.text,
            "created_at": self.created_at,
        }


def generate_response_id(responses: List[Response]) -> int:
    """Сгенерировать новый идентификатор ответа."""
    if not responses:
        return 1
    return max(response.id for response in responses) + 1


def is_message_answered(responses: List[Response], message_id: int) -> bool:
    """Проверить, есть ли уже ответ на сообщение с данным идентификатором."""
    return any(
        response.message is not None and response.message.id == message_id
        for response in responses
    )


def create_response(responses: List[Response], message: Message, text: str) -> Response:
    """Создать новый ответ на сообщение и закрыть само сообщение.

    Вызывает ValueError, если ответ на это сообщение уже существует.
    """
    if is_message_answered(responses, message.id):
        raise ValueError("Ответ на это сообщение уже существует")

    response = Response(generate_response_id(responses), message, text)
    responses.append(response)
    message.mark_closed()
    return response


def cancel_response(responses: List[Response], response_id: int) -> bool:
    """Удалить ответ по идентификатору, вернуть True при успехе."""
    for index, response in enumerate(responses):
        if response.id == response_id:
            del responses[index]
            return True
    return False


def get_responses_for_message(responses: List[Response], message_id: int) -> List[Response]:
    """Вернуть все ответы, относящиеся к заданному сообщению."""
    return [
        response
        for response in responses
        if response.message is not None and response.message.id == message_id
    ]


def iter_unanswered_messages(
    messages: List[Message],
    responses: List[Response],
) -> Iterator[Message]:
    """Вернуть генератор сообщений, на которые ещё не дан ответ."""
    answered_ids = {
        response.message.id for response in responses if response.message is not None
    }
    for message in messages:
        if message.id not in answered_ids:
            yield message


def show_responses(responses: List[Response]) -> None:
    """Вывести список ответов."""
    if not responses:
        print("Ответы отсутствуют")
        return
    for response in responses:
        print(response)
