from django.contrib import admin
from django import forms

from administration.kawaiibeats.models import SongMetadata
from administration.annoucements.models import Announcement, AnnouncementTranslation


# This class is for the announcement translation inline
class AnnouncementTranslationInline(admin.StackedInline):
    model = AnnouncementTranslation
    extra = 1
    fields = ("language", "content")


@admin.register(SongMetadata)
class SongMetadataAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "artists",
        "album",
        "spotify_id",
        "explicit",
        "release_date",
    )
    search_fields = ("title", "artists", "album", "spotify_id", "spotify_uri")
    list_filter = ("explicit",)
    ordering = ("-created_at",)
    date_hierarchy = "created_at"
    list_per_page = 20
    list_display_links = ("title", "artists")
    list_editable = ("explicit",)

    fieldsets = (
        (None, {"fields": ("title", "artists", "album")}),
        ("Spotify Information", {"fields": ("spotify_id", "spotify_uri")}),
        ("Album Art", {"fields": ("album_art_url", "custom_album_art")}),
        (
            "Additional Information",
            {"fields": ("duration_ms", "explicit", "release_date", "streaming_url")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("created_at", "updated_at")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        request._obj_ = None
        return qs

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field=from_field)
        if obj:
            request._obj_ = obj
        return obj


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = (
        "content_preview",
        "author",
        "is_public",
        "is_new",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_public", "is_new", "created_at")
    search_fields = ("content",)
    inlines = [AnnouncementTranslationInline]
    date_hierarchy = "created_at"

    fieldsets = (
        (None, {"fields": ("content", "author")}),
        ("Status", {"fields": ("is_public", "is_new")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
    readonly_fields = ("updated_at",)

    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content

    content_preview.short_description = "Content"
