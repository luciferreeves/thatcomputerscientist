from django.shortcuts import render
from announcements.functions import get_announcements
from blog.functions import get_posts
from internal.mal_wrapper import get_mal_recent_activity


def home(request):
    request.meta.title = "Home"
    context = {
        "announcements": get_announcements(),
        "recent_mal_activity": get_mal_recent_activity("crvs"),
        "recent_weblogs": get_posts(
            weblog_slug="shifoo",
            lang=request.LANGUAGE_CODE,
            per_page=3,
            order="desc",
        )["posts"],
    }
    return render(request, "core/home.html", context)
