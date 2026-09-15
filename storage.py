"""Сохранение и загрузка данных проекта в формате JSON."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


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
