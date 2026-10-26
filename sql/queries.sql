-- ==========================================
-- Сервис обратной связи: SQL-запросы проекта
-- Запросы проверены в SQLite CLI:
--     sqlite3 data/feedback.sqlite < sql/queries.sql
-- Значения в запросах (категории, даты, пороги) приведены для проверки;
-- в Django-представлениях они передаются параметрами "?".
-- ==========================================


-- ------------------------------------------
-- 1. ВЫБОРКА СПИСКОВ (SELECT)
-- ------------------------------------------

-- 1.1. Список сообщений: новые сверху (страница /messages/)
SELECT
    id,
    category,
    text,
    status,
    created_at
FROM messages
ORDER BY created_at DESC, id DESC;

-- 1.2. Список пользователей
SELECT
    id,
    name,
    email,
    role
FROM users
ORDER BY name;

-- 1.3. Список ответов (страница /responses/)
SELECT
    id,
    message_id,
    text,
    created_at
FROM responses
ORDER BY created_at DESC, id DESC;

-- 1.4. Список категорий, в которых есть сообщения (DISTINCT)
SELECT DISTINCT category
FROM messages
ORDER BY category;

-- 1.5. Последние два сообщения (ORDER BY + LIMIT + OFFSET)
SELECT
    id,
    category,
    created_at
FROM messages
ORDER BY created_at DESC, id DESC
LIMIT 2 OFFSET 0;


-- ------------------------------------------
-- 2. ФИЛЬТРАЦИЯ (WHERE)
-- ------------------------------------------

-- 2.1. Сообщения заданной категории
SELECT
    id,
    category,
    text,
    created_at
FROM messages
WHERE category = 'Жалоба'
ORDER BY created_at;

-- 2.2. Сообщения с признаком «новая»
SELECT
    id,
    text,
    created_at
FROM messages
WHERE status = 'новая'
ORDER BY created_at;

-- 2.3. Поиск по подстроке текста (LIKE).
-- В SQLite LIKE не различает регистр только у латиницы; в приложении для
-- русского текста используется функция lower_u(), см. feedback/views.py.
SELECT
    id,
    text
FROM messages
WHERE text LIKE '%войти%'
ORDER BY id;

-- 2.4. Несколько условий: категория, статус и дата (AND)
SELECT
    id,
    category,
    status,
    created_at
FROM messages
WHERE category = 'Общее'
  AND status = 'новая'
  AND created_at >= '2026-10-01'
ORDER BY created_at;

-- 2.5. Сообщения за период (BETWEEN) и в нескольких статусах (IN)
SELECT
    id,
    status,
    created_at
FROM messages
WHERE created_at BETWEEN '2026-09-01' AND '2026-09-30 23:59'
  AND status IN ('новая', 'закрыта')
ORDER BY created_at;


-- ------------------------------------------
-- 3. СОЕДИНЕНИЕ ТАБЛИЦ (JOIN)
-- ------------------------------------------

-- 3.1. Сообщения с именем автора (страницы /messages/, /messages/<id>/)
SELECT
    messages.id,
    messages.category,
    messages.text,
    messages.status,
    messages.created_at,
    users.name AS author_name,
    users.email AS author_email
FROM messages
JOIN users
    ON messages.user_id = users.id
ORDER BY messages.created_at DESC, messages.id DESC;

-- 3.2. Полная информация об ответе: ответ, сообщение и его автор
-- (страницы /responses/, /responses/<id>/)
SELECT
    responses.id,
    responses.text,
    responses.created_at,
    messages.id AS message_id,
    messages.text AS message_text,
    messages.category,
    users.name AS author_name
FROM responses
JOIN messages
    ON responses.message_id = messages.id
JOIN users
    ON messages.user_id = users.id
ORDER BY responses.created_at DESC, responses.id DESC;

-- 3.3. Сообщения без ответа (LEFT JOIN + IS NULL), страница /messages/unanswered/
SELECT
    messages.id,
    messages.category,
    messages.text,
    messages.status,
    messages.created_at,
    users.name AS author_name
FROM messages
JOIN users
    ON messages.user_id = users.id
LEFT JOIN responses
    ON responses.message_id = messages.id
WHERE responses.id IS NULL
ORDER BY messages.created_at;


-- ------------------------------------------
-- 4. АГРЕГАТНЫЕ ФУНКЦИИ
-- ------------------------------------------

-- 4.1. Общее количество сообщений (COUNT)
SELECT COUNT(*) AS messages_count
FROM messages;

-- 4.2. Количество сообщений без ответа (COUNT + LEFT JOIN)
SELECT COUNT(*) AS unanswered_count
FROM messages
LEFT JOIN responses
    ON responses.message_id = messages.id
WHERE responses.id IS NULL;

-- 4.3. Даты первого и последнего сообщения (MIN, MAX)
SELECT
    MIN(created_at) AS first_message,
    MAX(created_at) AS last_message
FROM messages;

-- 4.4. Средняя длина текста сообщения и количество авторов (AVG, COUNT DISTINCT)
SELECT
    ROUND(AVG(LENGTH(text)), 1) AS avg_text_length,
    COUNT(DISTINCT user_id) AS authors_count
FROM messages;


-- ------------------------------------------
-- 5. ГРУППИРОВКА (GROUP BY, HAVING)
-- ------------------------------------------

-- 5.1. Количество сообщений по статусам (страница /messages/statistics/)
SELECT
    status,
    COUNT(*) AS messages_count
FROM messages
GROUP BY status
ORDER BY messages_count DESC, status;

-- 5.2. Количество сообщений по категориям
SELECT
    category,
    COUNT(*) AS messages_count
FROM messages
GROUP BY category
ORDER BY messages_count DESC, category;

-- 5.3. Количество сообщений каждого автора, включая авторов без сообщений
-- (LEFT JOIN + GROUP BY)
SELECT
    users.name AS author_name,
    COUNT(messages.id) AS messages_count
FROM users
LEFT JOIN messages
    ON messages.user_id = users.id
GROUP BY users.id, users.name
ORDER BY messages_count DESC, users.name;

-- 5.4. Авторы, оставившие больше одного сообщения (HAVING)
SELECT
    users.name AS author_name,
    COUNT(messages.id) AS messages_count
FROM users
JOIN messages
    ON messages.user_id = users.id
GROUP BY users.id, users.name
HAVING COUNT(messages.id) > 1
ORDER BY messages_count DESC, users.name;

-- 5.5. Категории, в которых не менее двух сообщений (HAVING)
SELECT
    category,
    COUNT(*) AS messages_count
FROM messages
GROUP BY category
HAVING COUNT(*) >= 2
ORDER BY messages_count DESC;
