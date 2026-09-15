from messages import (
    CATEGORIES,
    add_message,
    count_messages_by_field,
    filter_messages_by_category,
    filter_messages_by_status,
    find_messages,
    get_message_status_text,
    sort_messages_by_date,
)
from responses import (
    cancel_response,
    create_response,
    get_responses_for_message,
    iter_unanswered_messages,
)
from storage import load_json, save_json
from users import add_user, can_create_message, find_user, get_user_role_description
from utils import input_choice, input_int, input_nonempty_str

USERS_FILE = "users.json"
MESSAGES_FILE = "messages.json"
RESPONSES_FILE = "responses.json"


def load_users() -> dict[int, dict]:
    """Загрузить пользователей и преобразовать список из JSON в словарь."""
    raw_users = load_json(USERS_FILE, default=[])
    return {
        user["id"]: {"name": user["name"], "email": user["email"], "role": user["role"]}
        for user in raw_users
    }


def save_users(users: dict[int, dict]) -> None:
    """Сохранить пользователей, преобразовав словарь в список для JSON."""
    raw_users = [{"id": user_id, **data} for user_id, data in users.items()]
    save_json(USERS_FILE, raw_users)


def seed_demo_data() -> tuple[dict[int, dict], list[dict], list[dict]]:
    """Создать демонстрационные данные, унаследованные из сценария ПР1."""
    users: dict[int, dict] = {}
    add_user(users, "Анна Иванова", "anna@example.com", "user")
    add_user(users, "Администратор", "admin@example.com", "admin")

    messages: list[dict] = []
    add_message(
        messages,
        user_id=1,
        category="Техническая поддержка",
        text="Не могу войти в личный кабинет, пишет ошибка 504",
    )

    responses: list[dict] = []
    return users, messages, responses


def show_users(users: dict[int, dict]) -> None:
    """Вывести список пользователей."""
    if not users:
        print("Пользователи отсутствуют")
        return
    for user_id, data in users.items():
        role_text = get_user_role_description(data["role"])
        print(f"[{user_id}] {data['name']} <{data['email']}> — {role_text}")


def show_messages(messages: list[dict]) -> None:
    """Вывести список сообщений."""
    if not messages:
        print("Сообщения отсутствуют")
        return
    for message in messages:
        status_text = get_message_status_text(message["status"])
        print(
            f"[{message['id']}] ({message['created_at']}) "
            f"{message['category']}: {message['text']} — {status_text}"
        )


def show_responses(responses: list[dict]) -> None:
    """Вывести список ответов."""
    if not responses:
        print("Ответы отсутствуют")
        return
    for response in responses:
        print(
            f"[{response['id']}] на сообщение {response['message_id']} "
            f"({response['created_at']}): {response['text']}"
        )


def handle_add_message(users: dict[int, dict], messages: list[dict]) -> None:
    """Обработать добавление нового сообщения."""
    user_id = input_int("ID пользователя: ")
    if user_id not in users:
        print("Пользователь с таким ID не найден")
        return
    if not can_create_message(users[user_id]["role"]):
        print("У пользователя нет прав для создания сообщения")
        return

    category = input_choice(f"Категория ({', '.join(CATEGORIES)}): ", CATEGORIES)
    text = input_nonempty_str("Текст сообщения: ")

    try:
        message = add_message(messages, user_id, category, text)
    except ValueError as error:
        print(f"Сообщение не может быть создано: {error}")
        return
    print(f"Сообщение успешно создано, ID: {message['id']}")


def handle_add_user(users: dict[int, dict]) -> None:
    """Обработать добавление нового пользователя."""
    name = input_nonempty_str("Имя пользователя: ")
    email = input_nonempty_str("Email: ")
    role = input_choice("Роль (user/admin): ", ["user", "admin"])
    user_id = add_user(users, name, email, role)
    print(f"Пользователь добавлен, ID: {user_id}")


def handle_create_response(messages: list[dict], responses: list[dict]) -> None:
    """Обработать создание ответа на сообщение."""
    message_id = input_int("ID сообщения: ")
    if not any(message["id"] == message_id for message in messages):
        print("Сообщение с таким ID не найдено")
        return
    text = input_nonempty_str("Текст ответа: ")

    try:
        response = create_response(responses, message_id, text)
    except ValueError as error:
        print(f"Ответ не может быть создан: {error}")
        return

    for message in messages:
        if message["id"] == message_id:
            message["status"] = "закрыта"
            break
    print(f"Ответ создан, ID: {response['id']}")


def handle_cancel_response(responses: list[dict]) -> None:
    """Обработать отмену ответа."""
    response_id = input_int("ID ответа: ")
    if cancel_response(responses, response_id):
        print("Ответ отменен")
    else:
        print("Ответ с таким ID не найден")


def handle_show_message_responses(responses: list[dict]) -> None:
    """Показать ответы на конкретное сообщение."""
    message_id = input_int("ID сообщения: ")
    show_responses(get_responses_for_message(responses, message_id))


def show_stats(messages: list[dict]) -> None:
    """Вывести статистику по сообщениям."""
    if not messages:
        print("Сообщения отсутствуют")
        return
    print("По статусам:")
    for status, count in count_messages_by_field(messages, "status").items():
        print(f"  {get_message_status_text(status)}: {count}")
    print("По категориям:")
    for category, count in count_messages_by_field(messages, "category").items():
        print(f"  {category}: {count}")


MENU = """
=== Сервис обратной связи ===
1. Показать пользователей
2. Найти пользователя по имени
3. Добавить пользователя
4. Показать сообщения
5. Найти сообщение по тексту
6. Отфильтровать сообщения по статусу
7. Отфильтровать сообщения по категории
8. Отсортировать сообщения по дате
9. Показать сообщения без ответа
10. Добавить сообщение
11. Показать ответы
12. Показать ответы на сообщение
13. Ответить на сообщение
14. Отменить ответ
15. Статистика по сообщениям
0. Выход
"""


def main() -> None:
    """Точка запуска приложения: меню и основной цикл взаимодействия."""
    users = load_users()
    messages = load_json(MESSAGES_FILE, default=[])
    responses = load_json(RESPONSES_FILE, default=[])

    if not users and not messages:
        users, messages, responses = seed_demo_data()

    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_users(users)
        elif choice == "2":
            query = input_nonempty_str("Подстрока имени: ")
            show_users({user["id"]: user for user in find_user(users, query)})
        elif choice == "3":
            handle_add_user(users)
        elif choice == "4":
            show_messages(messages)
        elif choice == "5":
            query = input_nonempty_str("Подстрока текста: ")
            show_messages(find_messages(messages, query))
        elif choice == "6":
            status = input_nonempty_str("Статус (новая/в обработке/закрыта): ")
            show_messages(filter_messages_by_status(messages, status))
        elif choice == "7":
            category = input_choice(f"Категория ({', '.join(CATEGORIES)}): ", CATEGORIES)
            show_messages(filter_messages_by_category(messages, category))
        elif choice == "8":
            show_messages(sort_messages_by_date(messages))
        elif choice == "9":
            show_messages(list(iter_unanswered_messages(messages, responses)))
        elif choice == "10":
            handle_add_message(users, messages)
        elif choice == "11":
            show_responses(responses)
        elif choice == "12":
            handle_show_message_responses(responses)
        elif choice == "13":
            handle_create_response(messages, responses)
        elif choice == "14":
            handle_cancel_response(responses)
        elif choice == "15":
            show_stats(messages)
        elif choice == "0":
            save_users(users)
            save_json(MESSAGES_FILE, messages)
            save_json(RESPONSES_FILE, responses)
            print("Данные сохранены. До свидания!")
            break
        else:
            print("Неизвестный пункт меню")


if __name__ == "__main__":
    main()
