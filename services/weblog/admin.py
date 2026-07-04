from django import forms
from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from services.weblog.models import (
    Category,
    CategoryTranslation,
    Comment,
    CommentVote,
    Post,
    PostTranslation,
    Tag,
    TagTranslation,
    Weblog,
)


class HiddenFromIndex(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}


class PostTranslationInline(admin.StackedInline):
    model = PostTranslation
    extra = 1
    fields = ("language", "title", "body")


class CategoryTranslationInline(admin.TabularInline):
    model = CategoryTranslation
    extra = 1
    fields = ("language", "name", "description")


class TagTranslationInline(admin.TabularInline):
    model = TagTranslation
    extra = 1
    fields = ("language", "name", "description")


class PostInline(admin.TabularInline):
    model = Post
    extra = 0
    can_delete = False
    fields = ("post_link", "author", "date", "is_public", "views")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Post")
    def post_link(self, obj):
        url = reverse("admin:services_post_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    can_delete = False
    fields = ("category_link", "slug", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Category")
    def category_link(self, obj):
        url = reverse("admin:services_category_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


class TagInline(admin.TabularInline):
    model = Tag
    extra = 0
    can_delete = False
    fields = ("tag_link", "slug", "created_at")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Tag")
    def tag_link(self, obj):
        url = reverse("admin:services_tag_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


@admin.register(Weblog)
class WeblogAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "post_count", "created_at")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PostInline, CategoryInline, TagInline]

    @admin.display(description="Posts")
    def post_count(self, obj):
        return obj.post_set.count()


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "category" in self.fields:
            self.fields["category"].required = False
        if self.instance.weblog_id:
            self.fields["category"].queryset = Category.objects.filter(weblog=self.instance.weblog)
            self.fields["tags"].queryset = Tag.objects.filter(weblog=self.instance.weblog)


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    can_delete = False
    max_num = 0
    fields = ("comment_link", "author_display", "created_at", "upvotes", "downvotes")
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False

    @admin.display(description="Comment")
    def comment_link(self, obj):
        url = reverse("admin:services_comment_change", args=[obj.pk])
        body = obj.body[:80] + ("..." if len(obj.body) > 80 else "")
        return format_html('<a href="{}">{}</a>', url, body)

    @admin.display(description="Author")
    def author_display(self, obj):
        if obj.user:
            return obj.user.username
        if obj.anonymous_user:
            return f"Anon: {obj.anonymous_user.name}"
        return "-"


@admin.register(Post)
class PostAdmin(HiddenFromIndex):
    form = PostAdminForm
    list_display = ("title", "weblog", "author", "date", "is_public", "views")
    list_filter = ("weblog", "is_public")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PostTranslationInline, CommentInline]
    date_hierarchy = "date"


@admin.register(Category)
class CategoryAdmin(HiddenFromIndex):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryTranslationInline]


@admin.register(Tag)
class TagAdmin(HiddenFromIndex):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TagTranslationInline]


@admin.register(Comment)
class CommentAdmin(HiddenFromIndex):
    list_display = ("post", "author_display", "created_at", "upvotes", "downvotes")
    list_filter = ("spam_status", "created_at")
    search_fields = ("body", "user__username")
    readonly_fields = ("created_at", "edited_at")

    @admin.display(description="Author")
    def author_display(self, obj):
        if obj.user:
            return obj.user.username
        if obj.anonymous_user:
            return obj.anonymous_user.name
        return "-"


@admin.register(CommentVote)
class CommentVoteAdmin(HiddenFromIndex):
    list_display = ("comment", "user", "vote_type", "created_at")
    list_filter = ("vote_type",)
    search_fields = ("comment__body", "user__username")
