from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from administration.annoucements.functions import get_announcements


@login_required
@user_passes_test(lambda u: u.is_superuser)
def home(request):
    title_map = {
        "en": "Announcements Manager",
        "ja": "アナウンスメントマネージャー",
    }
    request.meta.title = title_map.get(request.LANGUAGE_CODE)
    context = {
        "announcements": get_announcements(request.LANGUAGE_CODE),
    }

    return render(request, "administration/announcements.html", context)
