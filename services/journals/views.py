from __future__ import annotations

from datetime import date as date_type
from typing import Any, cast

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from core.translations import LANGUAGE_CHOICES
from services.journals.constants import (
    FORM_CHOICES,
    GENRE_CHOICES,
    MODE_CHOICES,
    MOOD_CHOICES,
    STATUS_CHOICES,
    TONE_CHOICES,
)
from services.journals.functions import (
    create_character,
    create_entry_tag,
    create_journal,
    create_journal_entry,
    create_volume,
    delete_character,
    delete_character_relationship,
    delete_entry_tag,
    delete_journal,
    delete_journal_entry,
    delete_volume,
    get_diary_calendar,
    get_journal_characters,
    get_journal_tags,
    get_journal_toc,
    get_journal_volumes,
    reorder_characters,
    reorder_entries,
    reorder_volumes,
    get_single_user_journal,
    get_user_journal_stats,
    get_user_journals,
    set_character_appearances,
    set_character_relationship,
    update_character,
    update_journal_entry,
    update_journal_settings,
    update_volume,
)


def _resolve_template(mode: str, tab_name: str, fallback: str) -> str:
    mode_template = f"journals/modes/{mode}/{tab_name}.html"
    try:
        get_template(mode_template)
        return mode_template
    except TemplateDoesNotExist:
        return fallback


def _journal_url(slug: str, tab: str = "entries", **params: str) -> str:
    base = f'/services/journals/{slug}?tab={tab}'
    for key, val in params.items():
        base += f"&{key}={val}"
    return base


@login_required
def journals(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    title_map = {
        "ja": "私のジャーナル",
        "en": "My Journals",
    }

    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    page = int(request.GET.get("page", 1))

    success, journals_result = get_user_journals(
        user, page, lang=request.LANGUAGE_CODE
    )
    if not success:
        messages.error(request, "Error loading journals.")
        journals_result = None

    success_stats, stats_result = get_user_journal_stats(user)
    if not success_stats or not isinstance(stats_result, dict):
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
def journal(request: HttpRequest, slug: str) -> HttpResponse:
    user = cast(User, request.user)
    success, journal_obj = get_single_user_journal(
        user, slug, lang=request.LANGUAGE_CODE
    )

    if not success:
        messages.error(request, "Journal not found.")
        return redirect("services:journals:journals")

    request.meta.title = journal_obj.name
    tab = request.GET.get("tab", "entries")
    entry_slug = request.GET.get("entry", "")
    is_entry_context = tab in ("edit", "settings") and bool(entry_slug)

    response = _handle_delete_actions(request, user, journal_obj, tab, entry_slug, is_entry_context)
    if response:
        return response

    if request.method == "POST":
        response = _handle_post(request, user, journal_obj, tab, entry_slug, is_entry_context)
        if response:
            return response

    context: dict[str, object] = {
        "journal": journal_obj,
        "languages": LANGUAGE_CHOICES,
        "tab": tab,
    }

    _add_entry_context(journal_obj, entry_slug, is_entry_context, context)
    if is_entry_context and "entry" not in context:
        messages.error(request, "Entry not found.")
        return redirect(_journal_url(journal_obj.slug))

    _add_mode_context(request, journal_obj, tab, context)

    template_name = _resolve_tab_template(journal_obj, tab, is_entry_context)

    return render(request, template_name, context)


def _handle_delete_actions(
    request: HttpRequest,
    user: User,
    journal_obj: Any,
    tab: str,
    entry_slug: str,
    is_entry_context: bool,
) -> HttpResponse | None:
    action = request.GET.get("action")
    if action != "delete":
        return None

    if not is_entry_context:
        if tab == "volumes":
            volume_id = request.GET.get("volume_id")
            if volume_id:
                ok, msg = delete_volume(user, journal_obj, int(volume_id))
                if ok:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
                return redirect(_journal_url(journal_obj.slug, "volumes"))

        if tab == "characters":
            character_id = request.GET.get("character_id")
            if character_id:
                ok, msg = delete_character(user, journal_obj, int(character_id))
                if ok:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
                return redirect(_journal_url(journal_obj.slug, "characters"))

            relationship_id = request.GET.get("relationship_id")
            if relationship_id:
                ok, msg = delete_character_relationship(user, journal_obj, int(relationship_id))
                if ok:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
                return redirect(_journal_url(journal_obj.slug, "characters"))

        if tab == "tags":
            tag_id = request.GET.get("tag_id")
            if tag_id:
                ok, msg = delete_entry_tag(user, journal_obj, int(tag_id))
                if ok:
                    messages.success(request, msg)
                else:
                    messages.error(request, msg)
                return redirect(_journal_url(journal_obj.slug, "tags"))

        delete_success, delete_message = delete_journal(user, journal_obj)
        if delete_success:
            messages.success(request, "Journal deleted successfully.")
        else:
            messages.error(request, delete_message)
        return redirect("services:journals:journals")

    del_success, del_message = delete_journal_entry(user, journal_obj, entry_slug)
    if del_success:
        messages.success(request, del_message)
    else:
        messages.error(request, del_message)
    return redirect(_journal_url(journal_obj.slug))


def _handle_post(
    request: HttpRequest,
    user: User,
    journal_obj: Any,
    tab: str,
    entry_slug: str,
    is_entry_context: bool,
) -> HttpResponse | None:
    if tab == "new":
        return _handle_new_entry(request, user, journal_obj)

    if tab == "settings" and not is_entry_context:
        return _handle_settings(request, user, journal_obj)

    if is_entry_context:
        return _handle_edit_entry(request, user, journal_obj, entry_slug)

    if tab == "volumes":
        return _handle_volume_post(request, user, journal_obj)

    if tab == "characters":
        return _handle_character_post(request, user, journal_obj)

    if tab == "tags":
        return _handle_tag_post(request, user, journal_obj)

    if tab == "entries" and request.POST.get("sub_action") == "reorder":
        entry_ids = [int(e) for e in request.POST.getlist("entry_order") if e.isdigit()]
        ok, msg = reorder_entries(user, journal_obj, entry_ids)
        if ok:
            messages.success(request, "Order saved.")
        else:
            messages.error(request, msg)
        return redirect(_journal_url(journal_obj.slug, "entries"))

    return None


def _handle_new_entry(request: HttpRequest, user: User, journal_obj: Any) -> HttpResponse:
    post = request.POST
    entry_title = post.get("title", "")
    entry_content = post.get("content", "")

    entry_date = None
    entry_date_str = post.get("entry_date", "").strip()
    if entry_date_str:
        try:
            entry_date = date_type.fromisoformat(entry_date_str)
        except ValueError:
            pass

    volume_id = None
    volume_id_str = post.get("volume", "").strip()
    if volume_id_str:
        try:
            volume_id = int(volume_id_str)
        except ValueError:
            pass

    character_ids = [int(c) for c in post.getlist("character_ids") if c.isdigit()]
    new_character_names = [n for n in post.getlist("new_character_names") if n.strip()]
    new_character_roles = post.getlist("new_character_roles")
    new_character_bios = post.getlist("new_character_bios")
    new_tag_names = [n for n in post.getlist("new_tag_names") if n.strip()]

    ok, result = create_journal_entry(
        journal_obj,
        entry_title,
        entry_content,
        is_draft=post.get("is_draft") == "on",
        mood=post.get("mood", ""),
        tone=post.get("tone", ""),
        genre=post.get("genre", ""),
        form=post.get("form", ""),
        summary=post.get("summary", ""),
        entry_date=entry_date,
        volume_id=volume_id,
        thumbnail=request.FILES.get("thumbnail"),
        character_ids=character_ids,
        new_character_names=new_character_names,
        new_character_roles=new_character_roles,
        new_character_bios=new_character_bios,
        new_tag_names=new_tag_names,
    )

    if ok:
        messages.success(request, "Journal entry created successfully.")
        return_tab = post.get("from", "entries")
        return redirect(_journal_url(journal_obj.slug, return_tab))
    messages.error(request, str(result))
    return redirect(f"{request.path}?tab=new")


def _handle_settings(request: HttpRequest, user: User, journal_obj: Any) -> HttpResponse:
    ok, msg = update_journal_settings(user, journal_obj, request.POST, request.FILES)
    if ok:
        messages.success(request, "Journal settings updated successfully.")
    else:
        messages.error(request, msg)
    return redirect(
        f'{reverse("services:journals:journal", kwargs={"slug": journal_obj.slug})}?tab=settings'
    )


def _handle_edit_entry(request: HttpRequest, user: User, journal_obj: Any, entry_slug: str) -> HttpResponse:
    ok, msg = update_journal_entry(user, journal_obj, entry_slug, request.POST, request.FILES)
    if ok:
        messages.success(request, msg)
        return redirect(_journal_url(journal_obj.slug))
    messages.error(request, msg)
    return redirect(f"{request.path}?tab=edit&entry={entry_slug}")


def _handle_volume_post(request: HttpRequest, user: User, journal_obj: Any) -> HttpResponse:
    post = request.POST
    sub_action = post.get("sub_action", "")

    if sub_action == "reorder":
        volume_ids = [int(v) for v in post.getlist("volume_order") if v.isdigit()]
        ok, msg = reorder_volumes(user, journal_obj, volume_ids)
        if ok:
            messages.success(request, "Volume order saved.")
        else:
            messages.error(request, msg)
        return redirect(_journal_url(journal_obj.slug, "volumes"))

    volume_id = post.get("volume_id")

    if volume_id:
        ok, result = update_volume(user, journal_obj, int(volume_id), post, request.FILES)
    else:
        ok, result = create_volume(
            user,
            journal_obj,
            post.get("title", ""),
            description=post.get("description", ""),
            cover_image=request.FILES.get("cover_image"),
        )

    if ok:
        messages.success(request, "Volume saved.")
    else:
        messages.error(request, str(result))
    return redirect(_journal_url(journal_obj.slug, "volumes"))


def _handle_character_post(request: HttpRequest, user: User, journal_obj: Any) -> HttpResponse:
    post = request.POST
    sub_action = post.get("sub_action", "")

    if sub_action == "reorder":
        character_ids = [int(c) for c in post.getlist("character_order") if c.isdigit()]
        ok, msg = reorder_characters(user, journal_obj, character_ids)
        if ok:
            messages.success(request, "Character order saved.")
        else:
            messages.error(request, msg)
        return redirect(_journal_url(journal_obj.slug, "characters"))

    if sub_action == "relationship":
        from_id = int(post.get("from_character", "0"))
        to_id = int(post.get("to_character", "0"))
        label = post.get("label", "")
        ok, result = set_character_relationship(user, journal_obj, from_id, to_id, label)
        if ok:
            messages.success(request, "Relationship saved.")
        else:
            messages.error(request, str(result))
        return redirect(_journal_url(journal_obj.slug, "characters"))

    if sub_action == "appearances":
        entry_slug = post.get("entry_slug", "")
        entry = journal_obj.entries.filter(slug=entry_slug).first()
        if entry:
            character_ids = [int(cid) for cid in post.getlist("character_ids")]
            ok, msg = set_character_appearances(user, journal_obj, entry, character_ids)
            if ok:
                messages.success(request, msg)
            else:
                messages.error(request, msg)
        return redirect(_journal_url(journal_obj.slug, "characters"))

    character_id = post.get("character_id")
    if character_id:
        ok, result = update_character(user, journal_obj, int(character_id), post, request.FILES)
    else:
        ok, result = create_character(
            user,
            journal_obj,
            post.get("name", ""),
            bio=post.get("bio", ""),
            role=post.get("role", "Supporting"),
            image=request.FILES.get("image"),
        )

    if ok:
        messages.success(request, "Character saved.")
    else:
        messages.error(request, str(result))
    return redirect(_journal_url(journal_obj.slug, "characters"))


def _handle_tag_post(request: HttpRequest, user: User, journal_obj: Any) -> HttpResponse:
    name = request.POST.get("name", "")
    ok, result = create_entry_tag(user, journal_obj, name)
    if ok:
        messages.success(request, "Tag created.")
    else:
        messages.error(request, str(result))
    return redirect(_journal_url(journal_obj.slug, "tags"))


def _add_entry_context(
    journal_obj: Any, entry_slug: str, is_entry_context: bool, context: dict[str, object]
) -> None:
    if not is_entry_context:
        return
    entry = (
        journal_obj.entries.prefetch_related("translations", "tags", "character_appearances__character")
        .filter(slug=entry_slug)
        .first()
    )
    if entry:
        context["entry"] = entry


def _add_mode_context(
    request: HttpRequest, journal_obj: Any, tab: str, context: dict[str, object]
) -> None:
    mode = journal_obj.mode

    if tab == "new" or (tab in ("edit", "settings") and "entry" in context):
        if mode in ("book", "light_novel"):
            context["volumes"] = get_journal_volumes(journal_obj)
            selected_volume = request.GET.get("volume", "")
            if selected_volume:
                context["selected_volume"] = selected_volume
        if mode == "short_stories":
            context["genre_choices"] = GENRE_CHOICES
            context["tone_choices"] = TONE_CHOICES
        if mode == "diary":
            context["mood_choices"] = MOOD_CHOICES
            selected_entry_date = request.GET.get("entry_date", "")
            if selected_entry_date:
                context["selected_entry_date"] = selected_entry_date
        if mode == "poetry":
            context["form_choices"] = FORM_CHOICES
            context["mood_choices"] = MOOD_CHOICES
        context["tags"] = get_journal_tags(journal_obj)
        if mode in ("book", "light_novel", "short_stories"):
            context["characters"] = get_journal_characters(journal_obj)
            if "entry" in context:
                context["entry_character_ids"] = list(
                    context["entry"].character_appearances.values_list("character_id", flat=True)
                )

    if tab == "entries" and mode in ("book", "light_novel"):
        from django.db.models import Prefetch  # noqa: F811

        context["volumes_with_entries"] = (
            journal_obj.volumes.prefetch_related(
                Prefetch("entries", queryset=journal_obj.entries.order_by("order"))
            ).order_by("order")
        )
        context["unassigned_entries"] = journal_obj.entries.filter(volume__isnull=True).order_by("order")

    if tab == "volumes" and mode in ("book", "light_novel"):
        context["volumes"] = get_journal_volumes(journal_obj)

    if tab == "characters" and mode in ("book", "light_novel", "short_stories"):
        context["characters"] = get_journal_characters(journal_obj)

    if tab == "tags":
        context["tags"] = get_journal_tags(journal_obj)

    if tab == "toc" and mode in ("book", "light_novel"):
        volumes, unassigned = get_journal_toc(journal_obj)
        context["toc_volumes"] = volumes
        context["toc_unassigned"] = unassigned

    if tab == "calendar" and mode == "diary":
        year = int(request.GET.get("year", timezone.now().year))
        month = int(request.GET.get("month", timezone.now().month))
        context["calendar"] = get_diary_calendar(journal_obj, year, month)

    if tab == "settings":
        context["status_choices"] = STATUS_CHOICES
        context["genre_choices"] = GENRE_CHOICES
        context["mode_choices"] = MODE_CHOICES


def _resolve_tab_template(journal_obj: Any, tab: str, is_entry_context: bool) -> str:
    if is_entry_context:
        return _resolve_template(journal_obj.mode, "edit_entry", "journals/edit_entry.html")

    match tab:
        case "settings":
            return "journals/settings.html"
        case "entries":
            return _resolve_template(journal_obj.mode, "entries", "journals/entries.html")
        case "new":
            return _resolve_template(journal_obj.mode, "new_entry", "journals/new_entry.html")
        case "volumes":
            return _resolve_template(journal_obj.mode, "volumes", "journals/volumes.html")
        case "characters":
            return _resolve_template(journal_obj.mode, "characters", "journals/characters.html")
        case "tags":
            return _resolve_template(journal_obj.mode, "tags", "journals/tags.html")
        case "toc":
            return _resolve_template(journal_obj.mode, "toc", "journals/toc.html")
        case "calendar":
            return _resolve_template(journal_obj.mode, "calendar", "journals/calendar.html")
        case _:
            return _resolve_template(journal_obj.mode, "journal", "journals/journal.html")


@login_required
def new_journal(request: HttpRequest) -> HttpResponse:
    user = cast(User, request.user)
    title_map = {
        "ja": "新しいジャーナル",
        "en": "New Journal",
    }

    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    context: dict[str, object] = {
        "mode_choices": MODE_CHOICES,
        "status_choices": STATUS_CHOICES,
        "genre_choices": GENRE_CHOICES,
    }

    if request.method == "POST":
        name = request.POST.get("name", "")
        description = request.POST.get("description", "")
        slug = request.POST.get("slug", "")
        private = request.POST.get("private") == "on"
        mode = request.POST.get("mode", "default")
        status = request.POST.get("status", "")
        genre = request.POST.get("genre", "")

        success, result = create_journal(
            user, name, description, private, slug,
            mode=mode, status=status, genre=genre,
        )

        if success:
            return redirect("services:journals:journals")
        else:
            messages.error(request, str(result))
            context["formdata"] = request.POST
            return render(request, "journals/new_journal.html", context)

    return render(request, "journals/new_journal.html", context)
