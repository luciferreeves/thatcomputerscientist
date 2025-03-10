from django.shortcuts import render
from thatcomputerscientist.utils import i18npatterns
from apps.administration.models import Announcement
from apps.journals.models import Journal
from internal.mal_wrapper import get_mal_recent_activity
from internal.weblog_utilities import recent_weblogs

MAL_USERNAME = "crvs"


def home(request):
    META = {
        "title": "Home",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)
    announcements = Announcement.objects.filter(is_public=True).order_by("-created_at")
    context = {
        "announcements": announcements,
        "recent_mal_activity": get_mal_recent_activity(MAL_USERNAME),
        "recent_weblogs": recent_weblogs(lang=LANGUAGE_CODE),
    }
    return render(request, f"{LANGUAGE_CODE}/core/home.html", context)


# My Pages
def my_journals(request):
    META = {
        "title": "My Journals",
    }
    request.meta.update(META)
    journals = Journal.objects.filter(owner=request.user).order_by("-created_at")
    context = {
        "journals": journals,
    }
    return render(request, f"shared/my/journals.html", context)
