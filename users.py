"""Функции для работы с пользователями сервиса обратной связи."""


def add_user(users: dict[int, dict], name: str, email: str, role: str) -> int:
    """Добавить пользователя в словарь users и вернуть его идентификатор."""
    user_id = max(users.keys(), default=0) + 1
    users[user_id] = {"name": name, "email": email, "role": role}
    return user_id


def find_user(users: dict[int, dict], query: str) -> list[dict]:
    """Найти пользователей, чье имя содержит подстроку query."""
    query_lower = query.lower()
    return [
        {"id": user_id, **data}
        for user_id, data in users.items()
        if query_lower in data["name"].lower()
    ]


def get_user_role_description(role: str) -> str:
    """Вернуть текстовое описание роли пользователя (функция из ПР1)."""
    if role == "admin":
        return "Администратор"
    return "Пользователь"


def can_create_message(role: str) -> bool:
    """Проверить, может ли пользователь с данной ролью создавать сообщения."""
    return role in ("user", "admin")
