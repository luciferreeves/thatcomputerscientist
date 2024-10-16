from django.shortcuts import render
from thatcomputerscientist.utils import i18npatterns


def home(request):
    META = {
        "title": "Home",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)

    return render(request, f"{LANGUAGE_CODE}/core/home.html")
