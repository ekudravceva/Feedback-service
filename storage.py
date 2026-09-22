"""Сохранение и загрузка объектов проекта в формате JSON."""

import json
from pathlib import Path
from typing import Any, List

from models import Message, Response, User

DATA_DIR = Path(__file__).parent / "data"

USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"
RESPONSES_FILE = "responses.json"


def load_json(filename: str, default: Any) -> Any:
    """Загрузить данные из JSON-файла в каталоге data/.

    Если файл отсутствует или содержит некорректный JSON,
    возвращается значение default, а программа не завершается аварийно.
    """
    path = DATA_DIR / filename
    try:
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        print(f"Предупреждение: файл {filename} поврежден, используются данные по умолчанию")
        return default


def save_json(filename: str, data: Any) -> None:
    """Сохранить данные в JSON-файл в каталоге data/."""
    DATA_DIR.mkdir(exist_ok=True)
    path = DATA_DIR / filename
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


def load_users() -> List[User]:
    """Загрузить пользователей из JSON и создать объекты User."""
    raw_users = load_json(USERS_FILE, default=[])
    return [User.from_data(data) for data in raw_users]


def save_users(users: List[User]) -> None:
    """Сохранить объекты User в JSON."""
    save_json(USERS_FILE, [user.to_data() for user in users])


def load_messages(users: List[User]) -> List[Message]:
    """Загрузить сообщения из JSON, связав их с объектами User."""
    raw_messages = load_json(MESSAGES_FILE, default=[])
    return [Message.from_data(data, users) for data in raw_messages]


def save_messages(messages: List[Message]) -> None:
    """Сохранить объекты Message в JSON."""
    save_json(MESSAGES_FILE, [message.to_data() for message in messages])


def load_responses(messages: List[Message]) -> List[Response]:
    """Загрузить ответы из JSON, связав их с объектами Message."""
    raw_responses = load_json(RESPONSES_FILE, default=[])
    return [Response.from_data(data, messages) for data in raw_responses]


def save_responses(responses: List[Response]) -> None:
    """Сохранить объекты Response в JSON."""
    save_json(RESPONSES_FILE, [response.to_data() for response in responses])
