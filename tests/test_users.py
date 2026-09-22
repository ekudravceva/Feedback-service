"""Тесты класса User и функций работы с коллекцией пользователей."""

from models import User
from models.users import add_user, find_user


def test_user_creation():
    user = User(1, "Иван Петров", "ivan@example.com", "user")
    assert user.id == 1
    assert user.name == "Иван Петров"
    assert user.email == "ivan@example.com"
    assert user.role == "user"


def test_user_str_contains_name_and_email():
    user = User(1, "Иван Петров", "ivan@example.com", "user")
    text = str(user)
    assert "Иван Петров" in text
    assert "ivan@example.com" in text


def test_user_can_create_message():
    user = User(1, "Иван Петров", "ivan@example.com", "user")
    assert user.can_create_message()


def test_add_user():
    users = []
    user = add_user(users, "Анна Иванова", "anna@example.com", "user")
    assert len(users) == 1
    assert user.id == 1


def test_find_user():
    users = []
    add_user(users, "Анна Иванова", "anna@example.com", "user")
    found = find_user(users, "анна")
    assert len(found) == 1


def test_user_from_data():
    data = {"id": 5, "name": "Сергей Сергеев", "email": "s@example.com", "role": "admin"}
    user = User.from_data(data)
    assert user.id == 5
    assert user.role == "admin"
