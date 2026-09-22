"""Класс сообщения и функции работы с коллекцией сообщений."""

from datetime import datetime
from typing import List, Optional, Tuple

from .users import User, find_user_by_id

CATEGORIES = [
    "Общее",
    "Техническая поддержка",
    "Предложение",
    "Жалоба",
]

STATUS_DESCRIPTIONS = {
    "новая": "Новое сообщение",
    "в обработке": "Сообщение в обработке",
    "закрыта": "Сообщение обработано",
}


def describe_status(status: str) -> str:
    """Вернуть текстовое описание статуса сообщения по его коду."""
    return STATUS_DESCRIPTIONS.get(status, "Неизвестный статус")


class Message:
    """Сообщение обратной связи, оставленное пользователем."""

    def __init__(
        self,
        message_id: int,
        author: Optional[User],
        category: str,
        text: str,
        status: str = "новая",
        created_at: Optional[str] = None,
    ) -> None:
        """Создать объект сообщения.

        Сохраняет идентификатор, автора (объект User), категорию,
        текст, статус и дату создания.
        """
        self.id = message_id
        self.author = author
        self.category = category
        self.text = text
        self.status = status
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M")

    def get_status_text(self) -> str:
        """Вернуть текстовое описание статуса конкретного сообщения."""
        return describe_status(self.status)

    def mark_closed(self) -> None:
        """Изменить статус сообщения на «закрыта» после получения ответа."""
        self.status = "закрыта"

    def matches(self, query: str) -> bool:
        """Проверить, содержит ли текст сообщения подстроку query."""
        return query.lower() in self.text.lower()

    def __str__(self) -> str:
        """Вернуть строковое представление сообщения."""
        return (
            f"[{self.id}] ({self.created_at}) {self.category}: "
            f"{self.text} — {self.get_status_text()}"
        )

    @staticmethod
    def validate(
        text: str,
        category: str,
        categories: List[str] = CATEGORIES,
    ) -> Tuple[bool, str]:
        """Проверить валидность текста и категории сообщения."""
        if len(text) < 10:
            return False, "Сообщение слишком короткое (минимум 10 символов)"
        if len(text) > 1000:
            return False, "Сообщение слишком длинное (максимум 1000 символов)"
        if category not in categories:
            return False, f"Категория '{category}' не существует"
        return True, "Сообщение валидно"

    @classmethod
    def from_data(cls, data: dict, users: List[User]) -> "Message":
        """Создать сообщение из набора данных, связав его с объектом User."""
        author = find_user_by_id(users, data["user_id"])
        return cls(
            data["id"],
            author,
            data["category"],
            data["text"],
            data["status"],
            data["created_at"],
        )

    def to_data(self) -> dict:
        """Преобразовать сообщение в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "user_id": self.author.id if self.author else None,
            "category": self.category,
            "text": self.text,
            "status": self.status,
            "created_at": self.created_at,
        }


def generate_message_id(messages: List[Message]) -> int:
    """Сгенерировать новый идентификатор сообщения."""
    if not messages:
        return 1
    return max(message.id for message in messages) + 1


def add_message(
    messages: List[Message],
    author: User,
    category: str,
    text: str,
) -> Message:
    """Проверить и добавить новое сообщение в коллекцию.

    Вызывает ValueError, если сообщение не проходит проверку валидности.
    """
    is_valid, validation_message = Message.validate(text, category)
    if not is_valid:
        raise ValueError(validation_message)

    message = Message(generate_message_id(messages), author, category, text)
    messages.append(message)
    return message


def find_messages(messages: List[Message], query: str) -> List[Message]:
    """Найти сообщения, содержащие подстроку query в тексте."""
    return [message for message in messages if message.matches(query)]


def filter_messages_by_status(messages: List[Message], status: str) -> List[Message]:
    """Отобрать сообщения с заданным статусом."""
    return [message for message in messages if message.status == status]


def filter_messages_by_category(messages: List[Message], category: str) -> List[Message]:
    """Отобрать сообщения заданной категории."""
    return list(filter(lambda message: message.category == category, messages))


def sort_messages_by_date(messages: List[Message], reverse: bool = False) -> List[Message]:
    """Отсортировать сообщения по дате создания."""
    return sorted(messages, key=lambda message: message.created_at, reverse=reverse)


def count_messages_by_field(messages: List[Message], field: str) -> dict:
    """Посчитать количество сообщений по значению заданного поля (статистика)."""
    stats: dict = {}
    for message in messages:
        value = getattr(message, field)
        stats[value] = stats.get(value, 0) + 1
    return stats


def find_message_by_id(messages: List[Message], message_id: int) -> Optional[Message]:
    """Найти сообщение по идентификатору."""
    for message in messages:
        if message.id == message_id:
            return message
    return None


def show_messages(messages: List[Message]) -> None:
    """Вывести список сообщений."""
    if not messages:
        print("Сообщения отсутствуют")
        return
    for message in messages:
        print(message)
