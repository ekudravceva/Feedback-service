from django.shortcuts import get_object_or_404, render

from responses.models import Response


def responses(request):
    responses_list = Response.objects.select_related(
        "message",
        "message__author",
    ).order_by("-created_at", "-pk")

    context = {
        "responses_list": responses_list,
    }

    return render(
        request,
        "responses/response_list.html",
        context,
    )


def response_detail(request, response_id):
    response = get_object_or_404(
        Response.objects.select_related("message", "message__author"),
        pk=response_id,
    )

    context = {
        "response": response,
    }

    return render(
        request,
        "responses/response_detail.html",
        context,
    )
