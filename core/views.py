from django.shortcuts import render
from announcements.functions import get_announcements
from blog.functions import get_recent_posts
from internal.mal_wrapper import get_mal_recent_activity


def home(request):
    request.meta.title = "Home"
    context = {
        "announcements": get_announcements(),
        "recent_mal_activity": get_mal_recent_activity("crvs"),
        "recent_weblogs": get_recent_posts(
            lang=request.LANGUAGE_CODE, amount=3, author_username="bobby"
        ),
    }
    return render(request, "core/home.html", context)
