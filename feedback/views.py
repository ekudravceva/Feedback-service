from django.shortcuts import render

from models.messages import find_message_by_id
from models.responses import get_responses_for_message
from storage import load_messages, load_responses, load_users


def messages(request):
    users_list = load_users()
    messages_list = load_messages(users_list)

    context = {
        "messages_list": messages_list,
    }

    return render(
        request,
        "feedback/message_list.html",
        context,
    )


def message_detail(request, message_id):
    users_list = load_users()
    messages_list = load_messages(users_list)
    message = find_message_by_id(messages_list, message_id)

    responses_list = load_responses(messages_list)
    message_responses = (
        get_responses_for_message(responses_list, message.id) if message else []
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
