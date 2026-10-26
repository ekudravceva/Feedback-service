import sqlite3

from django.shortcuts import render

from db.database import get_connection

LIST_SQL = """
    SELECT
        responses.id,
        responses.text,
        responses.created_at,
        messages.id AS message_id,
        messages.category,
        users.name AS author_name
    FROM responses
    JOIN messages
        ON responses.message_id = messages.id
    JOIN users
        ON messages.user_id = users.id
    ORDER BY responses.created_at DESC, responses.id DESC;
"""

DETAIL_SQL = """
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
    WHERE responses.id = ?;
"""


def responses(request):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        responses_list = conn.execute(LIST_SQL).fetchall()
    finally:
        conn.close()

    context = {
        "responses_list": responses_list,
    }

    return render(
        request,
        "responses/response_list.html",
        context,
    )


def response_detail(request, response_id):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    try:
        response = conn.execute(DETAIL_SQL, [response_id]).fetchone()
    finally:
        conn.close()

    context = {
        "response": response,
    }

    return render(
        request,
        "responses/response_detail.html",
        context,
        status=404 if response is None else 200,
    )
