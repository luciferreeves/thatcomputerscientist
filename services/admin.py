from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest
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


class JournalTranslationInline(admin.TabularInline[JournalTranslation, Journal]):
    model = JournalTranslation
    extra = 1
    fields = ("language", "name", "description")


class JournalEntryTranslationInline(admin.StackedInline[JournalEntryTranslation, JournalEntry]):
    model = JournalEntryTranslation
    extra = 1
    fields = ("language", "title", "content")


class JournalEntryInline(admin.TabularInline[JournalEntry, Journal]):
    model = JournalEntry
    extra = 0
    readonly_fields = ("title", "created_at", "updated_at")
    fields = ("title", "slug", "is_draft", "order", "created_at", "updated_at")
    can_delete = False

    def has_add_permission(self, request: HttpRequest, obj: Any = None) -> bool:
        return False


class VolumeInline(admin.TabularInline[Volume, Journal]):
    model = Volume
    extra = 0
    fields = ("title", "order", "description", "cover_image")


class CharacterInline(admin.TabularInline[Character, Journal]):
    model = Character
    extra = 0
    fields = ("name", "role", "order", "image")


class EntryTagInline(admin.TabularInline[EntryTag, Journal]):
    model = EntryTag
    extra = 0
    fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class CharacterAppearanceInline(admin.TabularInline[CharacterAppearance, JournalEntry]):
    model = CharacterAppearance
    extra = 0
    fields = ("character", "notes")
    raw_id_fields = ("character",)


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin[Journal]):
    list_display = ("name", "japanese_name", "owner", "mode", "status", "genre", "private", "created_at")
    list_filter = ("private", "mode", "status", "genre", "created_at", "owner")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [JournalTranslationInline, VolumeInline, CharacterInline, EntryTagInline, JournalEntryInline]
    filter_horizontal = ("shared_with",)
    fieldsets = (
        (None, {
            "fields": ("name", "slug", "description", "owner"),
        }),
        ("Mode & Classification", {
            "fields": ("mode", "status", "genre", "cover_image"),
        }),
        ("Access", {
            "fields": ("private", "shared_with"),
        }),
        ("Customization", {
            "fields": ("custom_css",),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Name (Japanese)")
    def japanese_name(self, obj: Journal) -> str:
        try:
            translation = obj.translations.filter(language="ja").first()
            if translation and translation.name:
                return translation.name
            return "-"
        except Exception:
            return "-"

    def get_queryset(self, request: HttpRequest) -> Any:
        return super().get_queryset(request)


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin[JournalEntry]):
    list_display = (
        "title", "japanese_title", "journal", "mode_display",
        "is_draft", "word_count", "order", "entry_date", "created_at",
    )
    list_filter = ("journal", "is_draft", "journal__mode", "genre", "mood", "created_at", "updated_at")
    list_editable = ("is_draft", "order")
    search_fields = ("title", "content", "journal__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [JournalEntryTranslationInline, CharacterAppearanceInline]
    filter_horizontal = ("tags",)
    raw_id_fields = ("journal", "volume")
    fieldsets = (
        (None, {
            "fields": ("journal", "title", "slug", "content"),
        }),
        ("Organization", {
            "fields": ("volume", "order", "is_draft", "entry_date"),
        }),
        ("Classification", {
            "fields": ("genre", "tone", "form", "mood", "tags"),
        }),
        ("Media", {
            "fields": ("summary", "thumbnail"),
        }),
        ("Stats", {
            "fields": ("word_count",),
        }),
    )
    readonly_fields = ("word_count",)

    @admin.display(description="Title (Japanese)")
    def japanese_title(self, obj: JournalEntry) -> str:
        try:
            translation = obj.translations.filter(language="ja").first()
            if translation and translation.title:
                return translation.title
            return "-"
        except Exception:
            return "-"

    @admin.display(description="Mode")
    def mode_display(self, obj: JournalEntry) -> str:
        return obj.journal.get_mode_display()

    def get_queryset(self, request: HttpRequest) -> Any:
        return super().get_queryset(request).select_related("journal", "volume")


@admin.register(Volume)
class VolumeAdmin(admin.ModelAdmin[Volume]):
    list_display = ("title", "journal", "order", "entry_count", "created_at")
    list_filter = ("journal",)
    list_editable = ("order",)
    search_fields = ("title", "journal__name")
    raw_id_fields = ("journal",)

    @admin.display(description="Entries")
    def entry_count(self, obj: Volume) -> int:
        return obj.entries.count()


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin[Character]):
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
class CharacterRelationshipAdmin(admin.ModelAdmin[CharacterRelationship]):
    list_display = ("from_character", "label", "to_character", "journal_display")
    list_filter = ("from_character__journal",)
    search_fields = ("from_character__name", "to_character__name", "label")
    raw_id_fields = ("from_character", "to_character")

    @admin.display(description="Journal")
    def journal_display(self, obj: CharacterRelationship) -> str:
        return obj.from_character.journal.name


@admin.register(CharacterAppearance)
class CharacterAppearanceAdmin(admin.ModelAdmin[CharacterAppearance]):
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
class EntryTagAdmin(admin.ModelAdmin[EntryTag]):
    list_display = ("name", "journal", "slug", "usage_count")
    list_filter = ("journal",)
    search_fields = ("name", "journal__name")
    prepopulated_fields = {"slug": ("name",)}
    raw_id_fields = ("journal",)

    @admin.display(description="Used by")
    def usage_count(self, obj: EntryTag) -> int:
        return obj.entries.count()
