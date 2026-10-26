-- ==========================================
-- Сервис обратной связи: структура базы данных
-- ==========================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user'
        CHECK (role IN ('user', 'admin'))
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'новая'
        CHECK (status IN ('новая', 'в обработке', 'закрыта')),
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Одно сообщение может иметь не более одного ответа (UNIQUE).
CREATE TABLE IF NOT EXISTS responses (
    id INTEGER PRIMARY KEY,
    message_id INTEGER NOT NULL UNIQUE,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
