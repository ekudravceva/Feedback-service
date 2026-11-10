import re
from datetime import date

from django.core.paginator import Paginator
from django.db.models import Count, F, Max, Min, Q
from django.shortcuts import get_object_or_404, render

from feedback.models import CATEGORIES, Message
from users.models import User

PAGE_SIZE = 5

# Допустимые значения параметра sort и соответствующие им поля модели:
# произвольный пользовательский ввод в order_by() не передаётся.
SORT_FIELDS = {
    "date": "-created_at",
    "date_asc": "created_at",
    "author": "author__name",
    "category": "category",
}


def _statuses():
    return [value for value, _ in Message.Status.choices]


def _parse_date(value):
    """Вернуть date из строки ГГГГ-ММ-ДД или None, если формат неверный."""
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def messages(request):
    category = request.GET.get("category", "").strip()
    status = request.GET.get("status", "").strip()
    author_id = request.GET.get("author", "").strip()
    hide_closed = request.GET.get("hide_closed") == "1"
    sort = request.GET.get("sort", "date")

    messages_qs = Message.objects.select_related("author")

    # Несколько условий фильтрации применяются последовательно (логика «И»).
    if category in CATEGORIES:
        messages_qs = messages_qs.filter(category=category)
    if status in _statuses():
        messages_qs = messages_qs.filter(status=status)
    if author_id.isdigit():
        messages_qs = messages_qs.filter(author_id=int(author_id))
    if hide_closed:
        messages_qs = messages_qs.exclude(status=Message.Status.CLOSED)

    sort_field = SORT_FIELDS.get(sort, SORT_FIELDS["date"])
    messages_qs = messages_qs.order_by(sort_field, "-pk")

    paginator = Paginator(messages_qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "messages_list": page_obj,
        "page_obj": page_obj,
        "categories": CATEGORIES,
        "statuses": _statuses(),
        "authors": User.objects.order_by("name"),
        "category": category,
        "status": status,
        "selected_author": author_id,
        "hide_closed": hide_closed,
        "sort": sort if sort in SORT_FIELDS else "date",
    }

    return render(
        request,
        "feedback/message_list.html",
        context,
    )


def message_detail(request, slug):
    message = get_object_or_404(
        Message.objects.select_related("author"),
        slug=slug,
    )

    context = {
        "message": message,
        # Обратная связь по related_name="responses".
        "message_responses": message.responses.all(),
    }

    return render(
        request,
        "feedback/message_detail.html",
        context,
    )


def unanswered(request):
    # LEFT JOIN с ответами: остаются сообщения, у которых ответов нет.
    messages_qs = (
        Message.objects
        .unanswered()
        .select_related("author")
        .order_by("created_at")
    )

    context = {
        "messages_list": messages_qs,
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

    parsed_date = None
    date_error = False
    if date_from:
        parsed_date = _parse_date(date_from)
        if parsed_date is None:
            date_from = ""
            date_error = True

    searched = any([category, status, query, date_from])
    results = []
    if searched:
        results = Message.objects.select_related("author")
        if category in CATEGORIES:
            results = results.filter(category=category)
        if status in _statuses():
            results = results.filter(status=status)
        if parsed_date is not None:
            results = results.filter(created_at__date__gte=parsed_date)
        if query:
            # LIKE/LOWER в SQLite различают регистр кириллицы, а iregex в
            # Django на SQLite выполняется регулярным выражением Python
            # (Unicode, без учёта регистра); спецсимволы экранируются.
            pattern = re.escape(query)
            results = results.filter(
                Q(text__iregex=pattern) | Q(author__name__iregex=pattern)
            )
        results = results.order_by("-created_at", "-pk")

    context = {
        "categories": CATEGORIES,
        "statuses": _statuses(),
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

    # Сводные показатели одним запросом (aggregate).
    total = Message.objects.aggregate(
        messages_count=Count("pk"),
        first_message=Min("created_at"),
        last_message=Max("created_at"),
    )

    # Авторы без сообщений тоже попадают в результат (запрос от User).
    by_author = (
        User.objects
        .annotate(
            messages_count=Count("messages"),
            author_name=F("name"),
        )
        .values("author_name", "messages_count")
        .order_by("-messages_count", "author_name")
    )

    context = {
        "total": total,
        "unanswered_count": Message.objects.unanswered().count(),
        "by_status": (
            Message.objects
            .values("status")
            .annotate(messages_count=Count("pk"))
            .order_by("-messages_count", "status")
        ),
        "by_category": (
            Message.objects
            .values("category")
            .annotate(messages_count=Count("pk"))
            .order_by("-messages_count", "category")
        ),
        "by_author": by_author,
        "more_than": more_than,
        "active_authors": by_author.filter(messages_count__gt=more_than),
    }

    return render(
        request,
        "feedback/statistics.html",
        context,
    )
