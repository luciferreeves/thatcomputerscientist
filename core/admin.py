from django.contrib import admin
from core.letters.models import Conversation, Letter


class LetterInline(admin.TabularInline):
    model = Letter
    extra = 0
    readonly_fields = ("sender", "content", "is_read", "created_at")


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("participant_one", "participant_two", "created_at", "updated_at")
    list_filter = ("created_at",)
    search_fields = (
        "participant_one__username",
        "participant_two__username",
    )
    inlines = [LetterInline]


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ("sender", "conversation", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "content")
    readonly_fields = ("created_at",)
