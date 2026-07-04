from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from services.admin_common import ADMIN_CSS, HiddenFromIndexMixin, LinkInline
from services.journals.models import (
    Character,
    CharacterAppearance,
    CharacterRelationship,
    EntryTag,
    Journal,
    JournalEntry,
    JournalEntryTranslation,
    JournalTranslation,
    Volume,
)


@dataclass(frozen=True)
class ModeShape:
    status: bool = False
    genre: bool = False
    cover: bool = False
    volumes: bool = False
    characters: bool = False
    entry_order: bool = False
    entry_date: bool = False
    entry_tags: bool = False
    entry_word_count: bool = False
    entry_summary: bool = False
    entry_thumbnail: bool = False
    entry_volume: bool = False
    entry_genre: bool = False
    entry_tone: bool = False
    entry_form: bool = False
    entry_mood: bool = False
    entry_characters: bool = False


_BOOK_SHAPE = ModeShape(
    status=True,
    genre=True,
    cover=True,
    volumes=True,
    characters=True,
    entry_order=True,
    entry_word_count=True,
    entry_summary=True,
    entry_thumbnail=True,
    entry_volume=True,
)

MODE_SHAPES: dict[str, ModeShape] = {
    "default": ModeShape(),
    "book": _BOOK_SHAPE,
    "light_novel": _BOOK_SHAPE,
    "short_stories": ModeShape(
        status=True,
        cover=True,
        characters=True,
        entry_order=True,
        entry_word_count=True,
        entry_summary=True,
        entry_thumbnail=True,
        entry_genre=True,
        entry_tone=True,
        entry_tags=True,
        entry_characters=True,
    ),
    "poetry": ModeShape(
        cover=True,
        entry_order=True,
        entry_form=True,
        entry_mood=True,
        entry_tags=True,
    ),
    "diary": ModeShape(
        entry_date=True,
        entry_mood=True,
        entry_tags=True,
        entry_word_count=True,
    ),
}


def shape_for(mode: str | None) -> ModeShape:
    return MODE_SHAPES.get(mode or "default", MODE_SHAPES["default"])


class JournalTranslationInline(LinkInline, admin.TabularInline[JournalTranslation, Journal]):
    model = JournalTranslation
    classes = ("collapse",)
    add_url_name = "admin:services_journaltranslation_add"
    add_fk = "journal"
    add_label = _("Add a translation")
    fields = ("language_display", "translation_link")
    readonly_fields = fields

    @admin.display(description=_("Language"))
    def language_display(self, obj: JournalTranslation) -> str:
        return obj.get_language_display()

    @admin.display(description=_("Translation"))
    def translation_link(self, obj: JournalTranslation) -> Any:
        url = reverse("admin:services_journaltranslation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name or "—")


class VolumeInline(LinkInline, admin.TabularInline[Volume, Journal]):
    model = Volume
    add_url_name = "admin:services_volume_add"
    add_fk = "journal"
    add_label = _("Add new volume")
    fields = ("volume_link", "order", "chapter_count")
    readonly_fields = fields

    @admin.display(description=_("Volume"))
    def volume_link(self, obj: Volume) -> Any:
        url = reverse("admin:services_volume_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    @admin.display(description=_("Chapters"))
    def chapter_count(self, obj: Volume) -> int:
        return obj.entries.count()


class CharacterInline(LinkInline, admin.TabularInline[Character, Journal]):
    model = Character
    add_url_name = "admin:services_character_add"
    add_fk = "journal"
    add_label = _("Add new character")
    fields = ("character_link", "role", "order")
    readonly_fields = fields

    @admin.display(description=_("Character"))
    def character_link(self, obj: Character) -> Any:
        url = reverse("admin:services_character_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


class EntryTagInline(LinkInline, admin.TabularInline[EntryTag, Journal]):
    model = EntryTag
    add_url_name = "admin:services_entrytag_add"
    add_fk = "journal"
    add_label = _("Add new tag")
    fields = ("tag_link", "slug", "usage_count")
    readonly_fields = fields

    @admin.display(description=_("Tag"))
    def tag_link(self, obj: EntryTag) -> Any:
        url = reverse("admin:services_entrytag_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)

    @admin.display(description=_("Used by"))
    def usage_count(self, obj: EntryTag) -> int:
        return obj.entries.count()


class JournalEntryInline(LinkInline, admin.TabularInline[JournalEntry, Journal]):
    model = JournalEntry
    fk_name = "journal"
    add_url_name = "admin:services_journalentry_add"
    add_fk = "journal"
    add_label = _("Add new entry")
    ordering = ("order", "-entry_date", "-created_at")

    def get_fields(self, request: HttpRequest, obj: Any = None) -> list[str]:
        shape = shape_for(obj.mode if obj else None)
        fields = ["entry_link"]
        if shape.entry_order:
            fields.append("order")
        if shape.entry_date:
            fields.append("entry_date")
        fields += ["is_draft", "updated_at"]
        return fields

    def get_readonly_fields(self, request: HttpRequest, obj: Any = None) -> tuple[str, ...]:
        return tuple(self.get_fields(request, obj))

    @admin.display(description=_("Entry"))
    def entry_link(self, obj: JournalEntry) -> Any:
        url = reverse("admin:services_journalentry_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)


class VolumeEntryInline(LinkInline, admin.TabularInline[JournalEntry, Volume]):
    model = JournalEntry
    fk_name = "volume"
    verbose_name = _("Chapter")
    verbose_name_plural = _("Chapters")
    add_url_name = "admin:services_journalentry_add"
    add_fk = "volume"
    add_label = _("Add new chapter")
    ordering = ("order",)
    fields = ("chapter_link", "order", "is_draft", "updated_at")
    readonly_fields = fields

    @admin.display(description=_("Chapter"))
    def chapter_link(self, obj: JournalEntry) -> Any:
        url = reverse("admin:services_journalentry_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)


class CharacterAppearanceInline(LinkInline, admin.TabularInline[CharacterAppearance, JournalEntry]):
    model = CharacterAppearance
    fk_name = "entry"
    add_url_name = "admin:services_characterappearance_add"
    add_fk = "entry"
    add_label = _("Add character appearance")
    fields = ("character_display", "appearance_link")
    readonly_fields = fields

    @admin.display(description=_("Character"))
    def character_display(self, obj: CharacterAppearance) -> str:
        return obj.character.name

    @admin.display(description=_("Appearance"))
    def appearance_link(self, obj: CharacterAppearance) -> Any:
        url = reverse("admin:services_characterappearance_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.notes[:60] if obj.notes else _("open"))


class JournalEntryTranslationInline(LinkInline, admin.TabularInline[JournalEntryTranslation, JournalEntry]):
    model = JournalEntryTranslation
    classes = ("collapse",)
    add_url_name = "admin:services_journalentrytranslation_add"
    add_fk = "journal_entry"
    add_label = _("Add a translation")
    fields = ("language_display", "translation_link")
    readonly_fields = fields

    @admin.display(description=_("Language"))
    def language_display(self, obj: JournalEntryTranslation) -> str:
        return obj.get_language_display()

    @admin.display(description=_("Translation"))
    def translation_link(self, obj: JournalEntryTranslation) -> Any:
        url = reverse("admin:services_journalentrytranslation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title or "—")


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin[Journal]):
    list_display = ("name", "japanese_name", "owner", "mode", "status", "private", "created_at")
    list_filter = ("private", "mode", "status", "genre", "created_at", "owner")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("shared_with",)

    class Media:
        css = ADMIN_CSS
        js = ("admin/journals/private_toggle.js",)

    def get_inlines(self, request: HttpRequest, obj: Any = None) -> list[Any]:
        shape = shape_for(obj.mode if obj else None)
        inlines: list[Any] = [JournalTranslationInline]
        if shape.volumes:
            inlines.append(VolumeInline)
        if shape.characters:
            inlines.append(CharacterInline)
        inlines.append(EntryTagInline)
        if obj is not None and not shape.volumes:
            inlines.append(JournalEntryInline)
        return inlines

    def get_fieldsets(self, request: HttpRequest, obj: Any = None) -> Any:
        shape = shape_for(obj.mode if obj else None)

        fieldsets: list[Any] = [
            (None, {"fields": ("name", "slug", "description", "owner")}),
        ]

        classification = ["mode"]
        if shape.status:
            classification.append("status")
        if shape.genre:
            classification.append("genre")
        if shape.cover:
            classification.append("cover_image")
        fieldsets.append((_("Mode"), {"fields": tuple(classification)}))

        fieldsets.append((_("Access"), {"fields": ("private", "shared_with")}))
        fieldsets.append((_("Customization"), {"fields": ("custom_css",), "classes": ("collapse",)}))
        return fieldsets

    @admin.display(description=_("Name (Japanese)"))
    def japanese_name(self, obj: Journal) -> str:
        translation = obj.translations.filter(language="ja").first()
        if translation and translation.name:
            return translation.name
        return "-"


@admin.register(JournalEntry)
class JournalEntryAdmin(HiddenFromIndexMixin, admin.ModelAdmin[JournalEntry]):
    list_display = (
        "title", "japanese_title", "journal", "mode_display",
        "is_draft", "order", "created_at",
    )
    list_filter = ("journal", "is_draft", "journal__mode", "created_at")
    list_editable = ("is_draft",)
    search_fields = ("title", "content", "journal__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("tags",)
    raw_id_fields = ("journal", "volume")
    readonly_fields = ("word_count",)

    class Media:
        css = ADMIN_CSS

    def get_form(self, request: HttpRequest, obj: Any = None, **kwargs: Any) -> Any:
        setattr(request, "_journalentry_obj", obj)
        return super().get_form(request, obj, **kwargs)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        volume_id = request.GET.get("volume")
        if volume_id and "journal" not in initial:
            volume = Volume.objects.filter(pk=volume_id).select_related("journal").first()
            if volume:
                initial["journal"] = volume.journal_id
        return initial

    def formfield_for_manytomany(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "tags":
            journal_id = self._current_journal_id(request)
            kwargs["queryset"] = (
                EntryTag.objects.filter(journal_id=journal_id) if journal_id else EntryTag.objects.none()
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def _current_journal_id(self, request: HttpRequest) -> Any:
        obj = getattr(request, "_journalentry_obj", None)
        if obj is not None:
            return obj.journal_id
        journal_id = request.GET.get("journal")
        if journal_id:
            return journal_id
        volume_id = request.GET.get("volume")
        if volume_id:
            volume = Volume.objects.filter(pk=volume_id).first()
            return volume.journal_id if volume else None
        return None

    def _shape(self, request: HttpRequest, obj: Any) -> ModeShape:
        if obj is not None:
            return shape_for(obj.journal.mode)
        journal_id = self._current_journal_id(request)
        if journal_id:
            journal = Journal.objects.filter(pk=journal_id).first()
            if journal:
                return shape_for(journal.mode)
        return shape_for(None)

    def get_inlines(self, request: HttpRequest, obj: Any = None) -> list[Any]:
        shape = self._shape(request, obj)
        inlines: list[Any] = [JournalEntryTranslationInline]
        if shape.entry_characters:
            inlines.append(CharacterAppearanceInline)
        return inlines

    def get_fieldsets(self, request: HttpRequest, obj: Any = None) -> Any:
        shape = self._shape(request, obj)

        fieldsets: list[Any] = [
            (None, {"fields": ("journal", "title", "slug", "content")}),
        ]

        organization: list[str] = []
        if shape.entry_volume:
            organization.append("volume")
        if shape.entry_order:
            organization.append("order")
        organization.append("is_draft")
        if shape.entry_date:
            organization.append("entry_date")
        fieldsets.append((_("Organization"), {"fields": tuple(organization)}))

        classification: list[str] = []
        if shape.entry_genre:
            classification.append("genre")
        if shape.entry_tone:
            classification.append("tone")
        if shape.entry_form:
            classification.append("form")
        if shape.entry_mood:
            classification.append("mood")
        if shape.entry_tags:
            classification.append("tags")
        if classification:
            fieldsets.append((_("Classification"), {"fields": tuple(classification)}))

        media: list[str] = []
        if shape.entry_summary:
            media.append("summary")
        if shape.entry_thumbnail:
            media.append("thumbnail")
        if media:
            fieldsets.append((_("Media"), {"fields": tuple(media)}))

        if shape.entry_word_count:
            fieldsets.append((_("Stats"), {"fields": ("word_count",)}))

        return fieldsets

    @admin.display(description=_("Title (Japanese)"))
    def japanese_title(self, obj: JournalEntry) -> str:
        translation = obj.translations.filter(language="ja").first()
        if translation and translation.title:
            return translation.title
        return "-"

    @admin.display(description=_("Mode"))
    def mode_display(self, obj: JournalEntry) -> str:
        return obj.journal.get_mode_display()

    def get_queryset(self, request: HttpRequest) -> Any:
        return super().get_queryset(request).select_related("journal", "volume")


@admin.register(Volume)
class VolumeAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Volume]):
    list_display = ("title", "journal", "order", "entry_count", "created_at")
    list_filter = ("journal",)
    list_editable = ("order",)
    search_fields = ("title", "journal__name")
    raw_id_fields = ("journal",)
    inlines = [VolumeEntryInline]

    class Media:
        css = ADMIN_CSS

    @admin.display(description=_("Entries"))
    def entry_count(self, obj: Volume) -> int:
        return obj.entries.count()


@admin.register(Character)
class CharacterAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Character]):
    list_display = ("name", "journal", "role", "order", "avatar_preview")
    list_filter = ("journal", "role")
    list_editable = ("role", "order")
    search_fields = ("name", "bio", "journal__name")
    raw_id_fields = ("journal",)

    @admin.display(description=_("Avatar"))
    def avatar_preview(self, obj: Character) -> str:
        if obj.image:
            return format_html('<img src="{}" width="32" height="32" style="border-radius:50%;object-fit:cover;" />', obj.image.url)
        return "-"


@admin.register(CharacterRelationship)
class CharacterRelationshipAdmin(HiddenFromIndexMixin, admin.ModelAdmin[CharacterRelationship]):
    list_display = ("from_character", "label", "to_character", "journal_display")
    list_filter = ("from_character__journal",)
    search_fields = ("from_character__name", "to_character__name", "label")
    raw_id_fields = ("from_character", "to_character")

    @admin.display(description=_("Journal"))
    def journal_display(self, obj: CharacterRelationship) -> str:
        return obj.from_character.journal.name


@admin.register(CharacterAppearance)
class CharacterAppearanceAdmin(HiddenFromIndexMixin, admin.ModelAdmin[CharacterAppearance]):
    list_display = ("character", "entry", "notes_preview")
    list_filter = ("character__journal",)
    search_fields = ("character__name", "entry__title", "notes")
    raw_id_fields = ("character", "entry")

    @admin.display(description=_("Notes"))
    def notes_preview(self, obj: CharacterAppearance) -> str:
        if obj.notes:
            return obj.notes[:80] + "..." if len(obj.notes) > 80 else obj.notes
        return "-"


@admin.register(EntryTag)
class EntryTagAdmin(HiddenFromIndexMixin, admin.ModelAdmin[EntryTag]):
    list_display = ("name", "journal", "slug", "usage_count")
    list_filter = ("journal",)
    search_fields = ("name", "journal__name")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("journal",)

    @admin.display(description=_("Used by"))
    def usage_count(self, obj: EntryTag) -> int:
        return obj.entries.count()


@admin.register(JournalTranslation)
class JournalTranslationAdmin(HiddenFromIndexMixin, admin.ModelAdmin[JournalTranslation]):
    list_display = ("journal", "language", "name")
    list_filter = ("language", "journal")
    search_fields = ("name", "journal__name")
    raw_id_fields = ("journal",)


@admin.register(JournalEntryTranslation)
class JournalEntryTranslationAdmin(HiddenFromIndexMixin, admin.ModelAdmin[JournalEntryTranslation]):
    list_display = ("journal_entry", "language", "title")
    list_filter = ("language",)
    search_fields = ("title", "journal_entry__title")
    raw_id_fields = ("journal_entry",)
