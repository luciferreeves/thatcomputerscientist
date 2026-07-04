from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from services.admin import ADMIN_CSS, HiddenFromIndexMixin
from authentication.models import AnonymousCommentUser, UserProfile


class UserProfileInline(admin.StackedInline[UserProfile, User]):
    model = UserProfile
    extra = 0
    fields = ("location", "bio", "avatar_url", "blinkie_url", "is_public", "email_public", "email_verified")


admin.site.unregister(User)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [UserProfileInline]
    change_list_template = "admin/authentication/users_change_list.html"

    class Media:
        css = ADMIN_CSS

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["users_active_tab"] = "registered"
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(AnonymousCommentUser)
class AnonymousCommentUserAdmin(admin.ModelAdmin[AnonymousCommentUser]):
    list_display = ("name", "email", "avatar_preview", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
    change_list_template = "admin/authentication/users_change_list.html"

    class Media:
        css = ADMIN_CSS

    def changelist_view(self, request: HttpRequest, extra_context: dict[str, Any] | None = None) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["users_active_tab"] = "anonymous"
        return super().changelist_view(request, extra_context=extra_context)

    @admin.display(description=_("Avatar"))
    def avatar_preview(self, obj: AnonymousCommentUser) -> Any:
        if obj.avatar:
            return format_html('<img src="{}" width="28" height="28" style="border-radius:50%;object-fit:cover;" />', obj.avatar)
        return "-"


@admin.register(UserProfile)
class UserProfileAdmin(HiddenFromIndexMixin, admin.ModelAdmin[UserProfile]):
    list_display = ("user", "location", "is_public", "email_verified")
    search_fields = ("user__username", "location", "bio")
    raw_id_fields = ("user",)
