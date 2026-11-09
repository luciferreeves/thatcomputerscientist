from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from services.admin import ADMIN_CSS, HiddenFromIndexMixin, LinkInline
from core.letters.models import Conversation, Letter, LetterAttachment


class LetterInline(LinkInline, admin.TabularInline[Letter, Conversation]):
    model = Letter
    add_url_name = "admin:core_letter_add"
    add_fk = "conversation"
    add_label = _("Add new letter")
    fields = ("letter_link", "sender", "is_read", "created_at")
    readonly_fields = fields

    @admin.display(description=_("Letter"))
    def letter_link(self, obj: Letter) -> Any:
        url = reverse("admin:core_letter_change", args=[obj.pk])
        preview = obj.content[:60] + ("…" if len(obj.content) > 60 else "")
        return format_html('<a href="{}">{}</a>', url, preview or _("(empty)"))


class LetterAttachmentInline(LinkInline, admin.TabularInline[LetterAttachment, Letter]):
    model = LetterAttachment
    fk_name = "letter"
    add_url_name = "admin:core_letterattachment_add"
    add_fk = "letter"
    add_label = _("Add new attachment")
    fields = ("attachment_link", "file_size", "content_type", "created_at")
    readonly_fields = fields

    @admin.display(description=_("Attachment"))
    def attachment_link(self, obj: LetterAttachment) -> Any:
        url = reverse("admin:core_letterattachment_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.original_name)


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin[Conversation]):
    list_display = ("participant_one", "participant_two", "letter_count", "updated_at")
    list_filter = ("created_at", "updated_at")
    search_fields = ("participant_one__username", "participant_two__username")
    raw_id_fields = ("participant_one", "participant_two")
    inlines = [LetterInline]

    class Media:
        css = ADMIN_CSS

    @admin.display(description=_("Letters"))
    def letter_count(self, obj: Conversation) -> int:
        return obj.letters.count()


@admin.register(Letter)
class LetterAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Letter]):
    list_display = ("sender", "conversation", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("sender__username", "content")
    readonly_fields = ("created_at",)
    raw_id_fields = ("conversation", "sender")
    inlines = [LetterAttachmentInline]

    class Media:
        css = ADMIN_CSS

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("sender", request.user.pk)
        return initial


@admin.register(LetterAttachment)
class LetterAttachmentAdmin(HiddenFromIndexMixin, admin.ModelAdmin[LetterAttachment]):
    list_display = ("original_name", "letter", "uploader", "file_size", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("original_name", "uploader__username")
    readonly_fields = ("created_at",)
    raw_id_fields = ("letter", "conversation", "uploader")
