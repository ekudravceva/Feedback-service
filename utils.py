"""Вспомогательные функции безопасного ввода данных."""


def input_int(prompt: str) -> int:
    """Запросить у пользователя целое число, повторяя запрос при ошибке."""
    while True:
        raw_value = input(prompt)
        try:
            return int(raw_value)
        except ValueError:
            print("Ошибка: введите целое число")


def input_nonempty_str(prompt: str) -> str:
    """Запросить у пользователя непустую строку."""
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Ошибка: строка не может быть пустой")


def input_choice(prompt: str, options: list[str]) -> str:
    """Запросить у пользователя значение из списка допустимых вариантов."""
    while True:
        value = input(prompt).strip()
        if value in options:
            return value
        print(f"Ошибка: допустимые значения: {', '.join(options)}")
