from django.contrib import admin
from authentication.models import UserProfile, AnonymousCommentUser

admin.site.register(UserProfile)


@admin.register(AnonymousCommentUser)
class AnonymousCommentUserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
