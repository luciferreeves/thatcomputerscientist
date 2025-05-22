from django.contrib import admin

from administration.kawaiibeats.models import SongMetadata


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
