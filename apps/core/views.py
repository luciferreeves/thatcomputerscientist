from django.shortcuts import render
from thatcomputerscientist.utils import i18npatterns
from apps.administration.models import Announcement
from internal.mal_wrapper import get_mal_recent_activity


MAL_USERNAME = "crvs"


def home(request):
    META = {
        "title": "Home",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)
    announcements = Announcement.objects.filter(is_public=True).order_by("-created_at")
    announcements = announcements if len(announcements) > 0 else None
    recent_mal_activity = get_mal_recent_activity(MAL_USERNAME)
    context = {
        "announcements": announcements,
        "recent_mal_activity": recent_mal_activity,
    }
    return render(request, f"{LANGUAGE_CODE}/core/home.html", context)
