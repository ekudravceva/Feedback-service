"""Функции для работы с сообщениями обратной связи."""

from datetime import datetime

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


def generate_message_id(messages: list[dict]) -> int:
    """Сгенерировать новый идентификатор сообщения."""
    if not messages:
        return 1
    return max(message["id"] for message in messages) + 1


def check_message_validity(
    text: str,
    category: str,
    categories: list[str] = CATEGORIES,
) -> tuple[bool, str]:
    """Проверить валидность текста и категории сообщения (функция из ПР1)."""
    if len(text) < 10:
        return False, "Сообщение слишком короткое (минимум 10 символов)"
    if len(text) > 1000:
        return False, "Сообщение слишком длинное (максимум 1000 символов)"
    if category not in categories:
        return False, f"Категория '{category}' не существует"
    return True, "Сообщение валидно"


def get_message_status_text(status: str) -> str:
    """Вернуть текстовое описание статуса сообщения (функция из ПР1)."""
    return STATUS_DESCRIPTIONS.get(status, "Неизвестный статус")


def add_message(
    messages: list[dict],
    user_id: int,
    category: str,
    text: str,
) -> dict:
    """Проверить и добавить новое сообщение в список messages.

    Вызывает ValueError, если сообщение не проходит проверку валидности.
    """
    is_valid, validation_message = check_message_validity(text, category)
    if not is_valid:
        raise ValueError(validation_message)

    message = {
        "id": generate_message_id(messages),
        "user_id": user_id,
        "category": category,
        "text": text,
        "status": "новая",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    messages.append(message)
    return message


def find_messages(messages: list[dict], query: str) -> list[dict]:
    """Найти сообщения, содержащие подстроку query в тексте."""
    query_lower = query.lower()
    return [message for message in messages if query_lower in message["text"].lower()]


def filter_messages_by_status(messages: list[dict], status: str) -> list[dict]:
    """Отобрать сообщения с заданным статусом."""
    return [message for message in messages if message["status"] == status]


def filter_messages_by_category(messages: list[dict], category: str) -> list[dict]:
    """Отобрать сообщения заданной категории."""
    return list(filter(lambda message: message["category"] == category, messages))


def sort_messages_by_date(messages: list[dict], reverse: bool = False) -> list[dict]:
    """Отсортировать сообщения по дате создания."""
    return sorted(messages, key=lambda message: message["created_at"], reverse=reverse)


def count_messages_by_field(messages: list[dict], field: str) -> dict[str, int]:
    """Посчитать количество сообщений по значению заданного поля (статистика)."""
    stats: dict[str, int] = {}
    for message in messages:
        value = message[field]
        stats[value] = stats.get(value, 0) + 1
    return stats
