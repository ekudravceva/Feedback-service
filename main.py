"""Точка запуска консольного приложения «Сервис обратной связи»."""

from typing import List, Tuple

from models import CATEGORIES, Message, Response, User
from models.messages import (
    add_message,
    count_messages_by_field,
    describe_status,
    filter_messages_by_category,
    filter_messages_by_status,
    find_message_by_id,
    find_messages,
    show_messages,
    sort_messages_by_date,
)
from models.responses import (
    cancel_response,
    create_response,
    get_responses_for_message,
    iter_unanswered_messages,
    show_responses,
)
from models.users import add_user, find_user, find_user_by_id, show_users
from storage import (
    load_messages,
    load_responses,
    load_users,
    save_messages,
    save_responses,
    save_users,
)
from utils import input_choice, input_int, input_nonempty_str


def seed_demo_data() -> Tuple[List[User], List[Message], List[Response]]:
    """Создать демонстрационные данные, унаследованные из сценария ПР1."""
    users: List[User] = []
    add_user(users, "Анна Иванова", "anna@example.com", "user")
    add_user(users, "Администратор", "admin@example.com", "admin")

    messages: List[Message] = []
    add_message(
        messages,
        author=users[0],
        category="Техническая поддержка",
        text="Не могу войти в личный кабинет, пишет ошибка 504",
    )

    responses: List[Response] = []
    return users, messages, responses


def handle_add_message(users: List[User], messages: List[Message]) -> None:
    """Обработать добавление нового сообщения."""
    user_id = input_int("ID пользователя: ")
    author = find_user_by_id(users, user_id)
    if author is None:
        print("Пользователь с таким ID не найден")
        return
    if not author.can_create_message():
        print("У пользователя нет прав для создания сообщения")
        return

    category = input_choice(f"Категория ({', '.join(CATEGORIES)}): ", CATEGORIES)
    text = input_nonempty_str("Текст сообщения: ")

    try:
        message = add_message(messages, author, category, text)
    except ValueError as error:
        print(f"Сообщение не может быть создано: {error}")
        return
    print(f"Сообщение успешно создано, ID: {message.id}")


def handle_add_user(users: List[User]) -> None:
    """Обработать добавление нового пользователя."""
    name = input_nonempty_str("Имя пользователя: ")
    email = input_nonempty_str("Email: ")
    role = input_choice("Роль (user/admin): ", ["user", "admin"])
    user = add_user(users, name, email, role)
    print(f"Пользователь добавлен, ID: {user.id}")


def handle_create_response(messages: List[Message], responses: List[Response]) -> None:
    """Обработать создание ответа на сообщение."""
    message_id = input_int("ID сообщения: ")
    message = find_message_by_id(messages, message_id)
    if message is None:
        print("Сообщение с таким ID не найдено")
        return
    text = input_nonempty_str("Текст ответа: ")

    try:
        response = create_response(responses, message, text)
    except ValueError as error:
        print(f"Ответ не может быть создан: {error}")
        return
    print(f"Ответ создан, ID: {response.id}")


def handle_cancel_response(responses: List[Response]) -> None:
    """Обработать отмену ответа."""
    response_id = input_int("ID ответа: ")
    if cancel_response(responses, response_id):
        print("Ответ отменен")
    else:
        print("Ответ с таким ID не найден")


def handle_show_message_responses(responses: List[Response]) -> None:
    """Показать ответы на конкретное сообщение."""
    message_id = input_int("ID сообщения: ")
    show_responses(get_responses_for_message(responses, message_id))


def show_stats(messages: List[Message]) -> None:
    """Вывести статистику по сообщениям."""
    if not messages:
        print("Сообщения отсутствуют")
        return
    print("По статусам:")
    for status, count in count_messages_by_field(messages, "status").items():
        print(f"  {describe_status(status)}: {count}")
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
    messages = load_messages(users)
    responses = load_responses(messages)

    if not users and not messages:
        users, messages, responses = seed_demo_data()

    while True:
        print(MENU)
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            show_users(users)
        elif choice == "2":
            query = input_nonempty_str("Подстрока имени: ")
            show_users(find_user(users, query))
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
            category = input_choice(
                f"Категория ({', '.join(CATEGORIES)}): ", CATEGORIES
            )
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
            save_messages(messages)
            save_responses(responses)
            print("Данные сохранены. До свидания!")
            break
        else:
            print("Неизвестный пункт меню")


if __name__ == "__main__":
    main()
