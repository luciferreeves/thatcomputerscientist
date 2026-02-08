from django.shortcuts import render
from django.http import HttpResponse
from administration.annoucements.functions import get_announcements
from authentication.functions import get_user_from_username
from blog.functions import get_posts
from internal.mal_wrapper import get_mal_recent_activity
import requests
import os

from services.journals.functions import get_latest_journal_entry


def home(request):
    title_map = {"en": "Home", "ja": "ホーム"}
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    success, recent_journal = get_latest_journal_entry(
        user=get_user_from_username("bobby"),
        slug="journal-of-random-thoughts",
        lang=request.LANGUAGE_CODE,
    )

    context = {
        "announcements": get_announcements(request.LANGUAGE_CODE),
        "recent_mal_activity": get_mal_recent_activity("crvs"),
        "recent_weblogs": get_posts(
            weblog_slug="shifoo",
            lang=request.LANGUAGE_CODE,
            per_page=3,
            order="desc",
        )["posts"],
        "recent_journal": recent_journal if success else None,
    }

    return render(request, "core/home.html", context)


def ignis_wrapper_temp(request, path):
    ignis_endpoint = os.getenv("IGNIS_CACHE_ENDPOINT", "shi.foo")
    url = f"https://{ignis_endpoint}/ignis/{path}"

    try:
        response = requests.get(url, timeout=10)
        return HttpResponse(
            response.content,
            content_type=response.headers.get(
                "Content-Type", "application/octet-stream"
            ),
        )
    except requests.RequestException:
        return HttpResponse("Error fetching resource", status=502)
