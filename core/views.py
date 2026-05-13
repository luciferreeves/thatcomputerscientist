from __future__ import annotations

import os
from typing import cast

import requests
from django.contrib.auth.models import AbstractUser
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.template.loader import get_template

from administration.annoucements.functions import get_announcements
from authentication.functions import get_user_from_username
from blog.functions import get_posts
from internal.mal_wrapper import get_mal_recent_activity
from internal.steam_wrapper import get_steam_screenshots
from services.journals.functions import (
    get_latest_journal_entry,
    get_journal,
    get_book_view_data,
    get_public_entry,
    get_public_character,
    get_entry_chapter_list,
    get_short_stories_view_data,
    get_short_stories_entry_data,
    get_poetry_view_data,
    get_poetry_entry_data,
    get_diary_view_data,
)



def home(request: HttpRequest) -> HttpResponse:
    title_map = {"en": "Home", "ja": "ホーム"}
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    success, recent_journal = get_latest_journal_entry(
        user=cast(AbstractUser, get_user_from_username("bobby")),
        slug="journal-of-random-thoughts",
        lang=request.LANGUAGE_CODE,
        count=1,
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


def screenshots(request: HttpRequest) -> HttpResponse:
    title_map = {"en": "Screenshots", "ja": "スクリーンショット"}
    request.meta.title = title_map.get(request.LANGUAGE_CODE)

    shots = get_steam_screenshots(os.getenv("STEAM_USERNAME", ""))
    return render(request, "core/screenshots.html", {"shots": shots})


def journal(request: HttpRequest, slug: str = "journal-of-random-thoughts") -> HttpResponse:
    page = int(request.GET.get("page", 1))
    entry_slug = request.GET.get("entry")
    character_id = request.GET.get("character")
    genre_filter = request.GET.get("genre", "")
    tone_filter = request.GET.get("tone", "")
    form_filter = request.GET.get("form", "")
    mood_filter = request.GET.get("mood", "")
    year_filter = request.GET.get("year", "")
    month_filter = request.GET.get("month", "")

    user = cast(AbstractUser, request.user) if request.user.is_authenticated else None
    success, journal_obj, entries = get_journal(
        slug, user=user, page=page, lang=request.LANGUAGE_CODE
    )

    if not success:
        raise Http404

    request.meta.title = journal_obj.name

    is_owner = request.user.is_authenticated and journal_obj.owner == request.user
    mode: str = journal_obj.mode
    is_book_mode = mode in ("book", "light_novel")
    owner_profile = journal_obj.owner.userprofile_set.first()

    if character_id and mode in ("book", "light_novel", "short_stories"):
        found, character, relationships, appearances = get_public_character(
            journal_obj, int(character_id),
        )
        if not found or character is None:
            raise Http404

        request.meta.title = f"{character.name} - {journal_obj.name}"

        context: dict[str, object] = {
            "journal": journal_obj,
            "character": character,
            "relationships": relationships,
            "appearances": appearances,
            "owner_profile": owner_profile,
        }

        if mode == "short_stories":
            return render(request, "journals/short_stories/characters.html", context)
        return render(request, "journals/books/characters.html", context)

    if entry_slug and mode != "diary":
        found, entry_obj, prev_entry, next_entry, chapter_number = get_public_entry(
            journal_obj, entry_slug, is_owner=is_owner, lang=request.LANGUAGE_CODE,
        )
        if not found or entry_obj is None:
            raise Http404

        request.meta.title = f"{entry_obj.title} - {journal_obj.name}"

        context = {
            "journal": journal_obj,
            "entry": entry_obj,
            "prev_entry": prev_entry,
            "next_entry": next_entry,
            "chapter_number": chapter_number,
            "owner_profile": owner_profile,
        }

        if is_book_mode:
            vols, unassigned = get_entry_chapter_list(journal_obj)
            context["volumes_with_entries"] = vols
            context["unassigned_entries"] = unassigned

        if mode == "short_stories":
            context.update(get_short_stories_entry_data(journal_obj, entry_obj, is_owner=is_owner))
        elif mode == "poetry":
            context.update(get_poetry_entry_data(journal_obj, entry_obj, is_owner=is_owner))

        if is_book_mode:
            template = "journals/books/entry.html"
        elif mode == "short_stories":
            template = "journals/short_stories/entry.html"
        elif mode == "poetry":
            template = "journals/poetry/entry.html"
        else:
            entry_template = f"journals/modes/{mode}/entry_read.html"
            try:
                get_template(entry_template)
                template = entry_template
            except TemplateDoesNotExist:
                template = "journals/entry_read.html"

        return render(request, template, context)

    context = {
        "journal": journal_obj,
        "entries": entries,
        "owner_profile": owner_profile,
    }

    if is_book_mode:
        context.update(get_book_view_data(journal_obj, is_owner=is_owner))
        template = "journals/books/main.html"
    elif mode == "short_stories":
        context.update(get_short_stories_view_data(journal_obj, is_owner=is_owner, genre=genre_filter, tone=tone_filter))
        template = "journals/short_stories/main.html"
    elif mode == "poetry":
        context.update(get_poetry_view_data(journal_obj, is_owner=is_owner, form=form_filter, mood=mood_filter, page=page))
        template = "journals/poetry/main.html"
    elif mode == "diary":
        try:
            year_int = int(year_filter) if year_filter else None
            month_int = int(month_filter) if month_filter else None
        except ValueError:
            year_int = None
            month_int = None
        selected_entry = None
        if entry_slug:
            from services.journals.models import JournalEntry as _JE
            entry_obj = _JE.objects.filter(journal=journal_obj, slug=entry_slug).first()
            if entry_obj and (is_owner or not entry_obj.is_draft):
                entry_obj.translate(request.LANGUAGE_CODE)
                selected_entry = entry_obj
                context["selected_entry"] = entry_obj
                request.meta.title = f"{entry_obj.title} - {journal_obj.name}"
        context.update(get_diary_view_data(journal_obj, is_owner=is_owner, year=year_int, month=month_int, current_entry=selected_entry, mood=mood_filter))
        template = "journals/diary/main.html"
    else:
        template = "journals/journal_view.html"
        mode_template = f"journals/modes/{mode}/journal_view.html"
        try:
            get_template(mode_template)
            template = mode_template
        except TemplateDoesNotExist:
            pass

    return render(request, template, context)


def ignis_wrapper_temp(request: HttpRequest, path: str) -> HttpResponse:
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
