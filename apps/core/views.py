from django.shortcuts import render
from thatcomputerscientist.utils import i18npatterns


def home(request):
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)

    return render(request, f"{LANGUAGE_CODE}/core/home.html")
