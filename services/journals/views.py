from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from services.journals.functions import (
    create_journal,
    get_user_journals,
    get_user_journal_stats,
)


@login_required
def journals(request):
    title_map = {
        "ja": "私のジャーナル",
        "en": "My Journals",
    }

    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    page = request.GET.get("page", 1)

    success, journals_result = get_user_journals(
        request.user, page, lang=request.LANGUAGE_CODE
    )
    if not success:
        messages.error(request, "Error loading journals.")
        journals_result = None

    success_stats, stats_result = get_user_journal_stats(request.user)
    if not success_stats:
        stats_result = {
            "private_journals_count": 0,
            "total_entries_count": 0,
        }

    context = {
        "journals": journals_result,
        "private_journals_count": stats_result["private_journals_count"],
        "total_entries_count": stats_result["total_entries_count"],
    }

    return render(request, "journals/journals.html", context)


@login_required
def new_journal(request):
    title_map = {
        "ja": "新しいジャーナル",
        "en": "New Journal",
    }

    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    if request.method == "POST":
        name = request.POST.get("name", "")
        description = request.POST.get("description", "")
        slug = request.POST.get("slug", "")
        private = request.POST.get("private") == "on"

        success, result = create_journal(request.user, name, description, private, slug)

        if success:
            return redirect("services:journals:journals")
        else:
            messages.error(request, result)
            return render(request, "journals/new.html", {"formdata": request.POST})

    return render(request, "journals/new.html")
