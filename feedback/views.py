import sqlite3
from datetime import date

from django.shortcuts import render

from db.database import get_connection
from models.messages import CATEGORIES, STATUS_DESCRIPTIONS

LIST_SQL = """
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
    ORDER BY messages.created_at DESC, messages.id DESC;
"""

DETAIL_SQL = """
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
    WHERE messages.id = ?;
"""

MESSAGE_RESPONSES_SQL = """
    SELECT
        id,
        text,
        created_at
    FROM responses
    WHERE message_id = ?
    ORDER BY id;
"""

UNANSWERED_SQL = """
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
"""

# Пустое значение параметра отключает соответствующее условие, поэтому
# текст запроса остаётся постоянным, а значения передаются только через "?".
SEARCH_SQL = """
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
    WHERE (? = '' OR messages.category = ?)
      AND (? = '' OR messages.status = ?)
      AND (? = '' OR lower_u(messages.text) LIKE '%' || lower_u(?) || '%')
      AND (? = '' OR messages.created_at >= ?)
    ORDER BY messages.created_at DESC, messages.id DESC;
"""

TOTAL_SQL = """
    SELECT
        COUNT(*) AS messages_count,
        MIN(created_at) AS first_message,
        MAX(created_at) AS last_message
    FROM messages;
"""

UNANSWERED_COUNT_SQL = """
    SELECT COUNT(*) AS unanswered_count
    FROM messages
    LEFT JOIN responses
        ON responses.message_id = messages.id
    WHERE responses.id IS NULL;
"""

BY_STATUS_SQL = """
    SELECT
        status,
        COUNT(*) AS messages_count
    FROM messages
    GROUP BY status
    ORDER BY messages_count DESC, status;
"""

BY_CATEGORY_SQL = """
    SELECT
        category,
        COUNT(*) AS messages_count
    FROM messages
    GROUP BY category
    ORDER BY messages_count DESC, category;
"""

BY_AUTHOR_SQL = """
    SELECT
        users.name AS author_name,
        COUNT(messages.id) AS messages_count
    FROM users
    LEFT JOIN messages
        ON messages.user_id = users.id
    GROUP BY users.id, users.name
    ORDER BY messages_count DESC, users.name;
"""

ACTIVE_AUTHORS_SQL = """
    SELECT
        users.name AS author_name,
        COUNT(messages.id) AS messages_count
    FROM users
    JOIN messages
        ON messages.user_id = users.id
    GROUP BY users.id, users.name
    HAVING COUNT(messages.id) > ?
    ORDER BY messages_count DESC, users.name;
"""


def _fetch_all(sql, params=()):
    """Выполнить запрос и вернуть все строки результата."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def _fetch_one(sql, params=()):
    """Выполнить запрос и вернуть одну строку (или None)."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()


def messages(request):
    context = {
        "messages_list": _fetch_all(LIST_SQL),
    }

    return render(
        request,
        "feedback/message_list.html",
        context,
    )


def message_detail(request, message_id):
    message = _fetch_one(DETAIL_SQL, [message_id])
    message_responses = (
        _fetch_all(MESSAGE_RESPONSES_SQL, [message_id]) if message else []
    )

    context = {
        "message": message,
        "message_responses": message_responses,
    }

    return render(
        request,
        "feedback/message_detail.html",
        context,
        status=404 if message is None else 200,
    )


def unanswered(request):
    context = {
        "messages_list": _fetch_all(UNANSWERED_SQL),
    }

    return render(
        request,
        "feedback/message_unanswered.html",
        context,
    )


def search(request):
    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    query = request.GET.get("q", "").strip()
    date_from = request.GET.get("date_from", "").strip()

    date_error = False
    if date_from:
        try:
            date.fromisoformat(date_from)
        except ValueError:
            date_from = ""
            date_error = True

    searched = any([category, status, query, date_from])
    results = []
    if searched:
        results = _fetch_all(
            SEARCH_SQL,
            [
                category, category,
                status, status,
                query, query,
                date_from, date_from,
            ],
        )

    context = {
        "categories": CATEGORIES,
        "statuses": list(STATUS_DESCRIPTIONS),
        "category": category,
        "status": status,
        "query": query,
        "date_from": date_from,
        "date_error": date_error,
        "searched": searched,
        "results": results,
    }

    return render(
        request,
        "feedback/message_search.html",
        context,
    )


def statistics(request):
    try:
        more_than = max(int(request.GET.get("more_than", "1")), 0)
    except ValueError:
        more_than = 1

    context = {
        "total": _fetch_one(TOTAL_SQL),
        "unanswered_count": _fetch_one(UNANSWERED_COUNT_SQL),
        "by_status": _fetch_all(BY_STATUS_SQL),
        "by_category": _fetch_all(BY_CATEGORY_SQL),
        "by_author": _fetch_all(BY_AUTHOR_SQL),
        "more_than": more_than,
        "active_authors": _fetch_all(ACTIVE_AUTHORS_SQL, [more_than]),
    }

    return render(
        request,
        "feedback/statistics.html",
        context,
    )
