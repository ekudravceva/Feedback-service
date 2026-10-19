from django.http import HttpResponse
from django.utils.html import escape

from homepage.views import page
from models.messages import find_message_by_id
from models.responses import is_message_answered
from storage import load_messages, load_responses, load_users

STATUS_BADGES = {
    "новая": "bg-primary",
    "в обработке": "bg-warning text-dark",
    "закрыта": "bg-success",
}


def messages(request):
    users_list = load_users()
    items = ""
    for message in load_messages(users_list):
        badge = STATUS_BADGES.get(message.status, "bg-secondary")
        items += f"""
        <li class="list-group-item d-flex justify-content-between">
            <a href="/messages/{message.id}/">
                [{message.id}] {escape(message.category)} –
                {escape(message.text[:60])}
            </a>
            <span class="badge {badge}">
                {escape(message.get_status_text())}
            </span>
        </li>
        """
    content = f"""
    <h1>Сообщения</h1>
    <ul class="list-group">{items}</ul>
    """
    return HttpResponse(page("Сервис обратной связи – сообщения", content))


def message_detail(request, message_id):
    users_list = load_users()
    messages_list = load_messages(users_list)
    message = find_message_by_id(messages_list, message_id)

    if message is None:
        content = """
        <h1 class="text-danger">Сообщение не найдено</h1>
        <a href="/messages/" class="btn btn-outline-secondary">
            ← к списку сообщений
        </a>
        """
        return HttpResponse(
            page("Сообщение не найдено", content),
            status=404,
        )

    responses_list = load_responses(messages_list)
    answered = is_message_answered(responses_list, message.id)
    answer = "есть" if answered else "нет"
    answer_badge = "bg-success" if answered else "bg-secondary"
    badge = STATUS_BADGES.get(message.status, "bg-secondary")
    author = escape(message.author.name) if message.author else "—"

    content = f"""
    <div class="card">
        <div class="card-body">
            <h5 class="card-title">Сообщение №{message.id}</h5>
            <p class="card-text">
                <strong>Автор:</strong> {author}
            </p>
            <p class="card-text">
                <strong>Категория:</strong> {escape(message.category)}
            </p>
            <p class="card-text">
                <strong>Дата:</strong> {escape(message.created_at)}
            </p>
            <p class="card-text">{escape(message.text)}</p>
            <p class="card-text">
                Статус:
                <span class="badge {badge}">
                    {escape(message.get_status_text())}
                </span>
            </p>
            <p class="card-text">
                Ответ на сообщение:
                <span class="badge {answer_badge}">{answer}</span>
            </p>
            <a href="/messages/" class="btn btn-outline-secondary">
                ← к списку сообщений
            </a>
        </div>
    </div>
    """
    return HttpResponse(
        page(f"Сообщение №{message.id}", content),
        status=200,
    )
