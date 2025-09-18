from django.contrib import admin
from services.journals.models import (
    Journal,
    JournalEntry,
    JournalTranslation,
    JournalEntryTranslation,
)


class JournalTranslationInline(admin.TabularInline):
    model = JournalTranslation
    extra = 1
    fields = ("language", "name", "description")


class JournalEntryTranslationInline(admin.StackedInline):
    model = JournalEntryTranslation
    extra = 1
    fields = ("language", "title", "content")


class JournalEntryInline(admin.TabularInline):
    model = JournalEntry
    extra = 0
    readonly_fields = ("title", "created_at", "updated_at")
    fields = ("title", "slug", "created_at", "updated_at")
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ("name", "japanese_name", "owner", "private", "created_at")
    list_filter = ("private", "created_at", "owner")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [JournalTranslationInline, JournalEntryInline]
    filter_horizontal = ("shared_with",)

    def japanese_name(self, obj):
        try:
            translation = obj.translations.filter(language="ja").first()
            if translation and translation.name:
                return translation.name
            return "-"
        except Exception:
            return "-"

    japanese_name.short_description = "Name (Japanese)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optionally filter by user if needed
        # if not request.user.is_superuser:
        #     qs = qs.filter(owner=request.user)
        return qs


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ("title", "japanese_title", "journal", "created_at", "updated_at")
    list_filter = ("journal", "created_at", "updated_at")
    search_fields = ("title", "content", "journal__name")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [JournalEntryTranslationInline]

    def japanese_title(self, obj):
        try:
            translation = obj.translations.filter(language="ja").first()
            if translation and translation.title:
                return translation.title
            return "-"
        except Exception:
            return "-"

    japanese_title.short_description = "Title (Japanese)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Optionally filter by user access if needed
        # if not request.user.is_superuser:
        #     qs = qs.filter(journal__owner=request.user)
        return qs
