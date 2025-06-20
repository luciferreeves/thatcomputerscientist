from django.shortcuts import render
from administration.annoucements.functions import get_announcements
from blog.functions import get_posts
from internal.mal_wrapper import get_mal_recent_activity


def home(request):
    title_map = {"en": "Home", "ja": "ホーム"}
    request.meta.title = title_map.get(request.LANGUAGE_CODE)
    context = {
        "announcements": get_announcements(request.LANGUAGE_CODE),
        "recent_mal_activity": get_mal_recent_activity("crvs"),
        "recent_weblogs": get_posts(
            weblog_slug="shifoo",
            lang=request.LANGUAGE_CODE,
            per_page=3,
            order="desc",
        )["posts"],
    }
    return render(request, "core/home.html", context)
