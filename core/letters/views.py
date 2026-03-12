import json

from django.conf import settings as django_settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe

from administration.emojis.functions import get_emoji_data

from core.letters.functions import (
    get_user_inbox,
    get_conversation_letters,
)


@login_required
def inbox(request):
    title_map = {"en": "Letters", "ja": "レター"}
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    page = request.GET.get("page", 1)
    success, inbox_result = get_user_inbox(request.user, page)

    context = {
        "conversations": inbox_result if success else None,
    }
    return render(request, "letters/inbox.html", context)


@login_required
def conversation(request, username):
    success, conv, letter_data = get_conversation_letters(request.user, username)

    if not success:
        messages.error(request, conv)
        return redirect("core:letters:inbox")

    request.meta.title = f"Letters - @{conv.other_user.username}"

    emoji_data = get_emoji_data()

    context = {
        "conversation": conv,
        "letters": letter_data["letters"],
        "has_more": letter_data["has_more"],
        "other_user": conv.other_user,
        "emoji_data_json": mark_safe(json.dumps(emoji_data)),
        "max_attachments": django_settings.LETTERS_MAX_ATTACHMENTS,
        "max_attachment_size": django_settings.LETTERS_MAX_ATTACHMENT_SIZE,
    }
    return render(request, "letters/conversation.html", context)


@login_required
def conversation_older(request, username):
    before_id = request.GET.get("before")
    if not before_id:
        return render(request, "letters/_partials/letter_rows.html", {
            "letters": [],
            "has_more": False,
        })

    success, conv, letter_data = get_conversation_letters(
        request.user, username, before_id=int(before_id)
    )

    if not success:
        return render(request, "letters/_partials/letter_rows.html", {
            "letters": [],
            "has_more": False,
        })

    return render(request, "letters/_partials/letter_rows.html", {
        "letters": letter_data["letters"],
        "has_more": letter_data["has_more"],
    })
