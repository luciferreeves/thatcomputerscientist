from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.annoucements.functions import (
    get_announcements,
    update_announcement,
    create_announcement,
)


@login_required
@user_passes_test(lambda u: u.is_superuser)
def home(request):
    title_map = {
        "en": "Announcements Manager",
        "ja": "アナウンスメントマネージャー",
    }
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    if request.method == "POST":
        mode = request.POST.get("mode")

        content = request.POST.get("content")
        is_new = request.POST.get("is_new") == "on"
        is_public = request.POST.get("is_public") == "on"

        if mode == "edit":
            announcement_id = request.POST.get("announcement_id")
            update_announcement(announcement_id, content, is_new, is_public)
        else:
            create_announcement(content, is_new, is_public)

    context = {
        "announcements": get_announcements(request.LANGUAGE_CODE),
    }

    return render(request, "administration/announcements.html", context)
