from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.http import HttpRequest
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from services.admin import ADMIN_CSS, HiddenFromIndexMixin, LinkInline
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


class PostTranslationInline(LinkInline, admin.TabularInline[PostTranslation, Post]):
    model = PostTranslation
    classes = ("collapse",)
    add_url_name = "admin:services_posttranslation_add"
    add_fk = "post"
    add_label = _("Add a translation")
    fields = ("language_display", "translation_link")
    readonly_fields = fields

    @admin.display(description=_("Language"))
    def language_display(self, obj: PostTranslation) -> str:
        return obj.get_language_display()

    @admin.display(description=_("Translation"))
    def translation_link(self, obj: PostTranslation) -> Any:
        url = reverse("admin:services_posttranslation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title or "—")


class CategoryTranslationInline(LinkInline, admin.TabularInline[CategoryTranslation, Category]):
    model = CategoryTranslation
    classes = ("collapse",)
    add_url_name = "admin:services_categorytranslation_add"
    add_fk = "category"
    add_label = _("Add a translation")
    fields = ("language_display", "translation_link")
    readonly_fields = fields

    @admin.display(description=_("Language"))
    def language_display(self, obj: CategoryTranslation) -> str:
        return obj.get_language_display()

    @admin.display(description=_("Translation"))
    def translation_link(self, obj: CategoryTranslation) -> Any:
        url = reverse("admin:services_categorytranslation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name or "—")


class TagTranslationInline(LinkInline, admin.TabularInline[TagTranslation, Tag]):
    model = TagTranslation
    classes = ("collapse",)
    add_url_name = "admin:services_tagtranslation_add"
    add_fk = "tag"
    add_label = _("Add a translation")
    fields = ("language_display", "translation_link")
    readonly_fields = fields

    @admin.display(description=_("Language"))
    def language_display(self, obj: TagTranslation) -> str:
        return obj.get_language_display()

    @admin.display(description=_("Translation"))
    def translation_link(self, obj: TagTranslation) -> Any:
        url = reverse("admin:services_tagtranslation_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name or "—")


class PostInline(LinkInline, admin.TabularInline[Post, Weblog]):
    model = Post
    add_url_name = "admin:services_post_add"
    add_fk = "weblog"
    add_label = _("Add new post")
    fields = ("post_link", "author", "date", "is_public", "views")
    readonly_fields = fields

    @admin.display(description=_("Post"))
    def post_link(self, obj: Post) -> Any:
        url = reverse("admin:services_post_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.title)


class CategoryInline(LinkInline, admin.TabularInline[Category, Weblog]):
    model = Category
    add_url_name = "admin:services_category_add"
    add_fk = "weblog"
    add_label = _("Add new category")
    fields = ("category_link", "slug", "created_at")
    readonly_fields = fields

    @admin.display(description=_("Category"))
    def category_link(self, obj: Category) -> Any:
        url = reverse("admin:services_category_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


class TagInline(LinkInline, admin.TabularInline[Tag, Weblog]):
    model = Tag
    add_url_name = "admin:services_tag_add"
    add_fk = "weblog"
    add_label = _("Add new tag")
    fields = ("tag_link", "slug", "created_at")
    readonly_fields = fields

    @admin.display(description=_("Tag"))
    def tag_link(self, obj: Tag) -> Any:
        url = reverse("admin:services_tag_change", args=[obj.pk])
        return format_html('<a href="{}">{}</a>', url, obj.name)


class CommentInline(LinkInline, admin.TabularInline[Comment, Post]):
    model = Comment
    add_url_name = "admin:services_comment_add"
    add_fk = "post"
    add_label = _("Add new comment")
    fields = ("comment_link", "author_display", "created_at", "upvotes", "downvotes")
    readonly_fields = fields

    @admin.display(description=_("Comment"))
    def comment_link(self, obj: Comment) -> Any:
        url = reverse("admin:services_comment_change", args=[obj.pk])
        body = obj.body[:80] + ("..." if len(obj.body) > 80 else "")
        return format_html('<a href="{}">{}</a>', url, body)

    @admin.display(description=_("Author"))
    def author_display(self, obj: Comment) -> str:
        if obj.user:
            return obj.user.username
        if obj.anonymous_user:
            return f"Anon: {obj.anonymous_user.name}"
        return "-"


@admin.register(Weblog)
class WeblogAdmin(admin.ModelAdmin[Weblog]):
    list_display = ("name", "owner", "post_count", "created_at")
    search_fields = ("name", "description", "owner__username")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PostInline, CategoryInline, TagInline]
    fieldsets = ((None, {"fields": ("name", "slug", "description", "owner")}),)

    class Media:
        css = ADMIN_CSS

    @admin.display(description=_("Posts"))
    def post_count(self, obj: Weblog) -> int:
        return obj.post_set.count()


@admin.register(Post)
class PostAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Post]):
    list_display = ("title", "weblog", "author", "date", "is_public", "views")
    list_filter = ("weblog", "is_public")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PostTranslationInline, CommentInline]
    date_hierarchy = "date"
    raw_id_fields = ("weblog", "author")
    filter_horizontal = ("tags",)
    readonly_fields = ("views",)
    fieldsets = (
        (None, {"fields": ("weblog", "title", "slug", "body")}),
        (_("Publishing"), {"fields": ("date", "author", "is_public")}),
        (_("Media"), {"fields": ("post_image", "image_url")}),
        (_("Taxonomy"), {"fields": ("category", "tags")}),
        (_("Stats"), {"fields": ("views",)}),
    )

    class Media:
        css = ADMIN_CSS

    def get_form(self, request: HttpRequest, obj: Any = None, **kwargs: Any) -> Any:
        setattr(request, "_post_obj", obj)
        return super().get_form(request, obj, **kwargs)

    def get_changeform_initial_data(self, request: HttpRequest) -> dict[str, Any]:
        initial = super().get_changeform_initial_data(request)
        initial.setdefault("author", request.user.pk)
        initial.setdefault("date", timezone.now())
        return initial

    def _current_weblog_id(self, request: HttpRequest) -> Any:
        obj = getattr(request, "_post_obj", None)
        if obj is not None:
            return obj.weblog_id
        return request.GET.get("weblog")

    def formfield_for_foreignkey(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "category":
            weblog_id = self._current_weblog_id(request)
            kwargs["queryset"] = (
                Category.objects.filter(weblog_id=weblog_id) if weblog_id else Category.objects.none()
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field: Any, request: HttpRequest, **kwargs: Any) -> Any:
        if db_field.name == "tags":
            weblog_id = self._current_weblog_id(request)
            kwargs["queryset"] = (
                Tag.objects.filter(weblog_id=weblog_id) if weblog_id else Tag.objects.none()
            )
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Category]):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryTranslationInline]
    raw_id_fields = ("weblog",)

    class Media:
        css = ADMIN_CSS


@admin.register(Tag)
class TagAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Tag]):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TagTranslationInline]
    raw_id_fields = ("weblog",)

    class Media:
        css = ADMIN_CSS


@admin.register(Comment)
class CommentAdmin(HiddenFromIndexMixin, admin.ModelAdmin[Comment]):
    list_display = ("post", "author_display", "created_at", "upvotes", "downvotes")
    list_filter = ("spam_status", "created_at")
    search_fields = ("body", "user__username")
    readonly_fields = ("created_at", "edited_at")
    raw_id_fields = ("post", "user", "anonymous_user", "parent")

    @admin.display(description=_("Author"))
    def author_display(self, obj: Comment) -> str:
        if obj.user:
            return obj.user.username
        if obj.anonymous_user:
            return obj.anonymous_user.name
        return "-"


@admin.register(CommentVote)
class CommentVoteAdmin(HiddenFromIndexMixin, admin.ModelAdmin[CommentVote]):
    list_display = ("comment", "user", "vote_type", "created_at")
    list_filter = ("vote_type",)
    search_fields = ("comment__body", "user__username")
    raw_id_fields = ("comment", "user")


@admin.register(PostTranslation)
class PostTranslationAdmin(HiddenFromIndexMixin, admin.ModelAdmin[PostTranslation]):
    list_display = ("post", "language", "title")
    list_filter = ("language",)
    search_fields = ("title", "post__title")
    raw_id_fields = ("post",)


@admin.register(CategoryTranslation)
class CategoryTranslationAdmin(HiddenFromIndexMixin, admin.ModelAdmin[CategoryTranslation]):
    list_display = ("category", "language", "name")
    list_filter = ("language",)
    search_fields = ("name", "category__name")
    raw_id_fields = ("category",)


@admin.register(TagTranslation)
class TagTranslationAdmin(HiddenFromIndexMixin, admin.ModelAdmin[TagTranslation]):
    list_display = ("tag", "language", "name")
    list_filter = ("language",)
    search_fields = ("name", "tag__name")
    raw_id_fields = ("tag",)
