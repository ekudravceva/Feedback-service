from datetime import datetime
import uuid

def generate_message_id():
    return str(uuid.uuid4())[:8]

categories = [
    "Общее",
    "Техническая поддержка",
    "Предложение",
    "Жалоба"
]
#демо данные о пользователе 
user_name = "Анна Иванова"
user_email = "anna@example.com"
user_role = "user" 

#тестовое сообщение
message_category = "Техническая поддержка"
message_text = "Не могу войти в личный кабинет, пишет ошибка 504"
message_status = "новая" 


def get_message_status_text(status):
    if status == "новая":
        return "Новое сообщение"
    elif status == "в обработке":
        return "Сообщение в обработке"
    elif status == "закрыта":
        return "Сообщение обработано"
    else:
        return "Неизвестный статус"


def check_message_validity(text, category):
    if len(text) < 10:
        return False, "Сообщение слишком короткое (минимум 10 символов)"
    
    if len(text) > 1000:
        return False, "Сообщение слишком длинное (максимум 1000 символов)"
    
    if category not in categories:
        return False, f"Категория '{category}' не существует"
    
    return True, "Сообщение валидно"


def get_user_role_description(role):
    if role == "admin":
        return "Администратор"
    else:
        return "Пользователь"


if user_role == "user" or user_role == "admin":
    can_create_message = True
else:
    can_create_message = False

print(f"\nПользователь: {user_name}")
print(f"Email: {user_email}")
print(f"Роль: {get_user_role_description(user_role)}")


print("Создание сообщения")
print(f"\nКатегория: {message_category}")
print(f"Текст: {message_text}")
print(f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}")


is_valid, validation_message = check_message_validity(message_text, message_category)

print(f"\nПроверка сообщения: {validation_message}")

if is_valid:
    message_id = generate_message_id()
    print(f"ID сообщения: {message_id}")
    print(f"Статус: {get_message_status_text(message_status)}")
    
    if can_create_message:
        print("\nСообщение успешно создано!")
        # Дополнительная логика для администраторов
        if user_role == "admin":
            print("(Администратор: вы можете сразу взять сообщение в обработку)")
        # Имитация сохранения
        print(f"\nСохранено: {message_id}_{message_category}_{datetime.now().strftime('%Y%m%d')}")
    else:
        print("\nУ вас нет прав для создания сообщения")
else:
    print("\nСообщение не может быть создано")
    print(f"Причина: {validation_message}")
