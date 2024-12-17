from django.shortcuts import render
from apps.journals.models import Journal
from thatcomputerscientist.utils import i18npatterns


# Create your views here.
def single_journal(request, slug):
    try:
        journal = Journal.objects.get(slug=slug)
    except Journal.DoesNotExist:
        journal = None
    META = {
        "title": f"Journal: {journal.name}" if journal else "Journal Not Found",
    }
    LANGUAGE_CODE = i18npatterns(request.LANGUAGE_CODE)
    request.meta.update(META)
    context = {
        "journal": journal,
    }
    return render(request, f"{LANGUAGE_CODE}/journals/single.html", context)
