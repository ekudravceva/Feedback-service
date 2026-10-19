from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.responses import find_response_by_id
from storage import load_messages, load_responses, load_users


def _load_responses():
    users_list = load_users()
    messages_list = load_messages(users_list)
    return load_responses(messages_list)


def responses(request):
    items = ""
    for response in _load_responses():
        message_id = response.message.id if response.message else "—"
        items += f"""
        <li class="list-group-item">
            <a href="/responses/{response.id}/">
                Ответ №{response.id} на сообщение {message_id}
            </a>
            <span class="text-muted">– {escape(response.created_at)}</span>
        </li>
        """
    content = f"""
    <h1>Ответы</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Сервис обратной связи – ответы", content))


def response_detail(request, response_id):
    response = find_response_by_id(_load_responses(), response_id)

    if response is None:
        content = """
        <h1 class="text-danger">Ответ не найден</h1>
        <a href="/responses/" class="btn btn-outline-secondary">
            ← к списку ответов
        </a>
        """
        return HttpResponse(
            page("Ответ не найден", content),
            status=404,
        )

    message = response.message
    if message:
        message_link = (
            f'<a href="/messages/{message.id}/">'
            f"Сообщение №{message.id}</a>: {escape(message.text)}"
        )
        author = escape(message.author.name) if message.author else "—"
    else:
        message_link = "—"
        author = "—"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Ответ №{response.id}</h5>
            <p class="card-text">Исходное сообщение: {message_link}</p>
            <p class="card-text">Автор сообщения: {author}</p>
            <p class="card-text">Дата ответа: {escape(response.created_at)}</p>
            <p class="card-text">{escape(response.text)}</p>
            <a href="/responses/" class="btn btn-outline-secondary">
                ← к списку ответов
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Ответ №{response.id}", content),
        status=200,
    )
