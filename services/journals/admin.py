from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html

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


class HiddenFromIndexMixin:
    def get_model_perms(self, request: HttpRequest) -> dict[str, bool]:
        return {}


class JournalTranslationInline(admin.TabularInline[JournalTranslation, Journal]):
    model = JournalTranslation
    extra = 1
    fields = ("language", "name", "description")
    classes = ("collapse",)


class JournalEntryTranslationInline(admin.StackedInline[JournalEntryTranslation, JournalEntry]):
    model = JournalEntryTranslation
    extra = 1
    fields = ("language", "title", "content")
    classes = ("collapse",)


class VolumeInline(admin.TabularInline[Volume, Journal]):
    model = Volume
    extra = 0
    can_delete = False
    fields = ("volume_link", "order", "chapter_count")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    @admin.display(description="Volume")
    def volume_link(self, obj: Volume) -> Any:
        url = reverse("admin:services_volume_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    @admin.display(description="Chapters")
    def chapter_count(self, obj: Volume) -> int:
        return obj.entries.count()


class CharacterInline(admin.TabularInline[Character, Journal]):
    model = Character
    extra = 0
    can_delete = False
    fields = ("character_link", "role", "order")
    readonly_fields = fields

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    @admin.display(description="Character")
    def character_link(self, obj: Character) -> Any:
        url = reverse("admin:services_character_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


class EntryTagInline(admin.TabularInline[EntryTag, Journal]):
    model = EntryTag
    extra = 1
    fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class JournalEntryInline(admin.TabularInline[JournalEntry, Journal]):
    model = JournalEntry
    extra = 0
    can_delete = False
    ordering = ("volume__order", "order", "-entry_date")

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False

    def get_fields(self, request: HttpRequest, obj: Any = None) -> list[str]:
        shape = shape_for(obj.mode if obj else None)
        fields = ["entry_link"]
        if shape.entry_volume:
            fields.append("volume_display")
        if shape.entry_order:
            fields.append("order")
        if shape.entry_date:
            fields.append("entry_date")
        fields += ["is_draft", "updated_at"]
        return fields

    def get_readonly_fields(self, request: HttpRequest, obj: Any = None) -> tuple[str, ...]:
        return tuple(self.get_fields(request, obj))

    @admin.display(description="Entry")
    def entry_link(self, obj: JournalEntry) -> Any:
        url = reverse("admin:services_journalentry_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)

    @admin.display(description="Volume")
    def volume_display(self, obj: JournalEntry) -> str:
        return obj.volume.title if obj.volume else "—"


class CharacterAppearanceInline(admin.TabularInline[CharacterAppearance, JournalEntry]):
    model = CharacterAppearance
    extra = 1
    fields = ("character", "notes")
    raw_id_fields = ("character",)


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin[Journal]):
    list_display = ("name", "japanese_name", "owner", "mode", "status", "private", "created_at")
    list_filter = ("private", "mode", "status", "genre", "created_at", "owner")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    filter_horizontal = ("shared_with",)

    class Media:
        js = ("admin/journals/private_toggle.js",)

    def get_inlines(self, request: HttpRequest, obj: Any = None) -> list[Any]:
        shape = shape_for(obj.mode if obj else None)
        inlines: list[Any] = [JournalTranslationInline]
        if shape.volumes:
            inlines.append(VolumeInline)
        if shape.characters:
            inlines.append(CharacterInline)
        inlines.append(EntryTagInline)
        if obj is not None:
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
        fieldsets.append(("Mode", {"fields": tuple(classification)}))

        fieldsets.append(("Access", {"fields": ("private", "shared_with")}))
        fieldsets.append(("Customization", {"fields": ("custom_css",), "classes": ("collapse",)}))
        return fieldsets

    @admin.display(description="Name (Japanese)")
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

    def get_inlines(self, request: HttpRequest, obj: Any = None) -> list[Any]:
        shape = shape_for(obj.journal.mode if obj else None)
        inlines: list[Any] = [JournalEntryTranslationInline]
        if shape.entry_characters:
            inlines.append(CharacterAppearanceInline)
        return inlines

    def get_fieldsets(self, request: HttpRequest, obj: Any = None) -> Any:
        shape = shape_for(obj.journal.mode if obj else None)

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
        fieldsets.append(("Organization", {"fields": tuple(organization)}))

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
            fieldsets.append(("Classification", {"fields": tuple(classification)}))

        media: list[str] = []
        if shape.entry_summary:
            media.append("summary")
        if shape.entry_thumbnail:
            media.append("thumbnail")
        if media:
            fieldsets.append(("Media", {"fields": tuple(media)}))

        if shape.entry_word_count:
            fieldsets.append(("Stats", {"fields": ("word_count",)}))

        return fieldsets

    @admin.display(description="Title (Japanese)")
    def japanese_title(self, obj: JournalEntry) -> str:
        translation = obj.translations.filter(language="ja").first()
        if translation and translation.title:
            return translation.title
        return "-"

    @admin.display(description="Mode")
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

    @admin.display(description="Entries")
    def entry_count(self, obj: Volume) -> int:
        return obj.entries.count()


@admin.register(Character)
class CharacterAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Character]):
    list_display = ("name", "journal", "role", "order", "avatar_preview")
    list_filter = ("journal", "role")
    list_editable = ("role", "order")
    search_fields = ("name", "bio", "journal__name")
    raw_id_fields = ("journal",)

    @admin.display(description="Avatar")
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

    @admin.display(description="Journal")
    def journal_display(self, obj: CharacterRelationship) -> str:
        return obj.from_character.journal.name


@admin.register(CharacterAppearance)
class CharacterAppearanceAdmin(HiddenFromIndexMixin, admin.ModelAdmin[CharacterAppearance]):
    list_display = ("character", "entry", "notes_preview")
    list_filter = ("character__journal",)
    search_fields = ("character__name", "entry__title", "notes")
    raw_id_fields = ("character", "entry")

    @admin.display(description="Notes")
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

    @admin.display(description="Used by")
    def usage_count(self, obj: EntryTag) -> int:
        return obj.entries.count()
