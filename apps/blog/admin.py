from django.contrib import admin
from django import forms
from .models import (
    AnonymousCommentUser,
    Category,
    Comment,
    Post,
    Tag,
    Weblog,
    PostTranslation,
    CategoryTranslation,
    TagTranslation,
)


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


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.weblog_id:
            self.fields["category"].queryset = Category.objects.filter(
                weblog=self.instance.weblog
            )
            self.fields["tags"].queryset = Tag.objects.filter(
                weblog=self.instance.weblog
            )


from django.utils.safestring import mark_safe


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    class CommentInline(admin.TabularInline):
        model = Comment
        extra = 0
        readonly_fields = (
            "comment_display",
            "user_display",
            "created_at",
            "edited",
            "edited_at",
        )
        fields = ("comment_display", "user_display", "created_at", "edited")
        exclude = ("body", "user", "anonymous_user", "level", "parent")
        can_delete = False
        max_num = 0

        def user_display(self, obj):
            if obj.user:
                return mark_safe(
                    f'<a href="/admin/advanced/auth/user/{obj.user.id}/">{obj.user.username}</a>'
                )
            elif obj.anonymous_user:
                return mark_safe(
                    f'<a href="/admin/advanced/blog/anonymouscommentuser/{obj.anonymous_user.id}/">'
                    f"Anonymous: {obj.anonymous_user.name}</a>"
                )
            return "None"

        user_display.short_description = "User"

        def comment_display(self, obj):
            return mark_safe(
                f'<a href="/admin/advanced/blog/comment/{obj.id}/">{obj.body[:100]}{"..." if len(obj.body) > 100 else ""}</a>'
            )

        comment_display.short_description = "Comment"

    form = PostAdminForm
    list_display = (
        "title",
        "weblog",
        "author",
        "date",
        "is_public",
        "views",
        "comment_count",
    )
    list_filter = ("weblog", "is_public", "category", "tags")
    search_fields = ("title", "body")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [PostTranslationInline, CommentInline]
    date_hierarchy = "date"

    def comment_count(self, obj):
        return obj.comments.count()

    comment_count.short_description = "Comments"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None:
            form.base_fields["category"].queryset = Category.objects.none()
            form.base_fields["tags"].queryset = Tag.objects.none()
        return form

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category" and request._obj_ is not None:
            kwargs["queryset"] = Category.objects.filter(weblog=request._obj_.weblog)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        request._obj_ = None
        return qs

    def get_object(self, request, object_id, from_field=None):
        obj = super().get_object(request, object_id, from_field=from_field)
        if obj:
            request._obj_ = obj
        return obj


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CategoryTranslationInline]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "weblog", "created_at")
    list_filter = ("weblog",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [TagTranslationInline]


@admin.register(Weblog)
class WeblogAdmin(admin.ModelAdmin):
    class PostInline(admin.TabularInline):
        model = Post
        extra = 0
        readonly_fields = ("title", "author", "date", "is_public", "views")
        can_delete = False
        fields = ("title", "author", "date", "is_public", "views")

        def has_add_permission(self, request, obj=None):
            return False

    class CategoryInline(admin.TabularInline):
        model = Category
        extra = 0
        readonly_fields = ("name", "created_at")
        can_delete = False
        fields = ("name", "created_at")

        def has_add_permission(self, request, obj=None):
            return False

    class TagInline(admin.TabularInline):
        model = Tag
        extra = 0
        readonly_fields = ("name", "created_at")
        can_delete = False
        fields = ("name", "created_at")

        def has_add_permission(self, request, obj=None):
            return False

    list_display = ("name", "owner", "created_at")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PostInline, CategoryInline, TagInline]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "get_author", "created_at", "edited")
    list_filter = ("edited", "created_at")
    search_fields = ("body", "user__username", "anonymous_user__name")
    readonly_fields = ("created_at", "edited", "edited_at")

    def get_author(self, obj):
        return obj.user.username if obj.user else obj.anonymous_user.name

    get_author.short_description = "Author"


@admin.register(AnonymousCommentUser)
class AnonymousCommentUserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
    readonly_fields = ("created_at",)
