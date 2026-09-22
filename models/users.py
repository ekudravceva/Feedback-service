"""Класс пользователя и функции работы с коллекцией пользователей."""

from typing import List, Optional

ROLE_DESCRIPTIONS = {
    "user": "Пользователь",
    "admin": "Администратор",
}


def describe_role(role: str) -> str:
    """Вернуть текстовое описание роли пользователя по её коду."""
    return ROLE_DESCRIPTIONS.get(role, "Неизвестная роль")


class User:
    """Пользователь сервиса обратной связи."""

    def __init__(self, user_id: int, name: str, email: str, role: str) -> None:
        """Создать объект пользователя.

        Сохраняет переданные данные в атрибутах объекта.
        """
        self.id = user_id
        self.name = name
        self.email = email
        self.role = role

    def get_role_description(self) -> str:
        """Вернуть текстовое описание роли конкретного пользователя."""
        return describe_role(self.role)

    def can_create_message(self) -> bool:
        """Проверить, может ли пользователь создавать сообщения."""
        return self.role in ("user", "admin")

    def __str__(self) -> str:
        """Вернуть строковое представление пользователя."""
        return f"[{self.id}] {self.name} <{self.email}> — {self.get_role_description()}"

    @classmethod
    def from_data(cls, data: dict) -> "User":
        """Создать пользователя из набора данных (например, из JSON)."""
        return cls(data["id"], data["name"], data["email"], data["role"])

    def to_data(self) -> dict:
        """Преобразовать пользователя в словарь для сохранения в JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "role": self.role,
        }


def generate_user_id(users: List[User]) -> int:
    """Сгенерировать новый идентификатор пользователя."""
    if not users:
        return 1
    return max(user.id for user in users) + 1


def add_user(users: List[User], name: str, email: str, role: str) -> User:
    """Создать объект User, добавить его в коллекцию и вернуть его."""
    user = User(generate_user_id(users), name, email, role)
    users.append(user)
    return user


def find_user(users: List[User], query: str) -> List[User]:
    """Найти пользователей, чьё имя содержит подстроку query."""
    query_lower = query.lower()
    return [user for user in users if query_lower in user.name.lower()]


def find_user_by_id(users: List[User], user_id: int) -> Optional[User]:
    """Найти пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    return None


def show_users(users: List[User]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователи отсутствуют")
        return
    for user in users:
        print(user)
