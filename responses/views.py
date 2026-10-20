from django.shortcuts import render

from models.responses import find_response_by_id
from storage import load_messages, load_responses, load_users


def _load_responses():
    users_list = load_users()
    messages_list = load_messages(users_list)
    return load_responses(messages_list)


def responses(request):
    context = {
        "responses_list": _load_responses(),
    }

    return render(
        request,
        "responses/response_list.html",
        context,
    )


def response_detail(request, response_id):
    response = find_response_by_id(_load_responses(), response_id)

    context = {
        "response": response,
    }

    return render(
        request,
        "responses/response_detail.html",
        context,
        status=404 if response is None else 200,
    )
