from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from core.translations import LANGUAGE_CHOICES
from services.journals.functions import (
    create_journal,
    create_journal_entry,
    get_user_journals,
    get_single_user_journal,
    get_user_journal_stats,
    update_journal_settings,
    update_journal_entry,
    delete_journal,
    delete_journal_entry,
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
def journal(request, slug):
    success, journal = get_single_user_journal(
        request.user, slug, lang=request.LANGUAGE_CODE
    )

    if not success:
        messages.error(request, "Journal not found.")
        return redirect("services:journals:journals")

    request.meta.title = journal.name
    tab = request.GET.get("tab", "entries")
    entry_slug = request.GET.get("entry", "")
    is_entry_context = tab in ("edit", "settings") and entry_slug

    if request.GET.get("action") == "delete" and not is_entry_context:
        delete_success, delete_message = delete_journal(request.user, journal)
        if delete_success:
            messages.success(request, "Journal deleted successfully.")
        else:
            messages.error(request, delete_message)
        return redirect("services:journals:journals")

    if is_entry_context and request.GET.get("action") == "delete":
        del_success, del_message = delete_journal_entry(
            request.user, journal, entry_slug
        )
        if del_success:
            messages.success(request, del_message)
        else:
            messages.error(request, del_message)
        return redirect(f"/services/journals/{journal.slug}?tab=entries")

    if request.method == "POST" and tab == "new":
        entry_title = request.POST.get("title", "")
        entry_content = request.POST.get("content", "")

        create_success, create_message = create_journal_entry(
            journal, entry_title, entry_content
        )

        if create_success:
            messages.success(request, "Journal entry created successfully.")
            return redirect(f"/services/journals/{journal.slug}?tab=entries")
        else:
            messages.error(request, create_message)
            return redirect(f"{request.path}?tab=new")

    if request.method == "POST" and tab == "settings" and not is_entry_context:
        update_success, update_message = update_journal_settings(
            request.user, journal, request.POST
        )
        if update_success:
            messages.success(request, "Journal settings updated successfully.")
        else:
            messages.error(request, update_message)
        return redirect(
            f'{reverse("services:journals:journal", kwargs={"slug": journal.slug})}?tab=settings'
        )

    if request.method == "POST" and is_entry_context:
        update_success, update_message = update_journal_entry(
            request.user, journal, entry_slug, request.POST
        )
        if update_success:
            messages.success(request, update_message)
            return redirect(f"/services/journals/{journal.slug}?tab=entries")
        else:
            messages.error(request, update_message)
            return redirect(f"{request.path}?tab=edit&entry={entry_slug}")

    context = {
        "journal": journal,
        "languages": LANGUAGE_CHOICES,
    }

    if is_entry_context:
        entry = (
            journal.entries.prefetch_related("translations")
            .filter(slug=entry_slug)
            .first()
        )
        if not entry:
            messages.error(request, "Entry not found.")
            return redirect(f"/services/journals/{journal.slug}?tab=entries")
        context["entry"] = entry

    if is_entry_context:
        template_name = "journals/edit_entry.html"
    else:
        match tab:
            case "settings":
                template_name = "journals/settings.html"
            case "entries":
                template_name = "journals/entries.html"
            case "new":
                template_name = "journals/new_entry.html"
            case _:
                template_name = "journals/journal.html"

    return render(request, template_name, context)


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

    return render(request, "journals/new_journal.html")
