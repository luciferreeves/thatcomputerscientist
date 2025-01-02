import hashlib
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.utils.text import slugify

UPLOAD_ROOT = "images/"
LANGUAGE_CHOICES = [
    ("en", "English"),
    ("ja", "Japanese"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("zh", "Chinese"),
    ("ko", "Korean"),
]


class Translation(models.Model):
    """Base abstract model for translations"""

    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CategoryTranslation(Translation):
    category = models.ForeignKey(
        "Category", on_delete=models.CASCADE, related_name="translations"
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["category", "language"]

    def __str__(self):
        return f"{self.category.name} - {self.get_language_display()}"


class TagTranslation(Translation):
    tag = models.ForeignKey(
        "Tag", on_delete=models.CASCADE, related_name="translations"
    )
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["tag", "language"]


class PostTranslation(Translation):
    post = models.ForeignKey(
        "Post", on_delete=models.CASCADE, related_name="translations"
    )
    title = models.CharField(max_length=100)
    body = models.TextField()

    class Meta:
        unique_together = ["post", "language"]


class TranslatableMixin:
    def get_translation(self, language_code):
        try:
            return self.translations.get(language=language_code)
        except self.translations.model.DoesNotExist:
            return None

    def translate(self, field_name, language_code="en"):
        translation = self.get_translation(language_code)
        if translation and hasattr(translation, field_name):
            return getattr(translation, field_name)
        return getattr(self, field_name)


class Weblog(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    name_ja = models.CharField(
        max_length=50, blank=True
    )  # Kept for backward compatibility
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["weblog", "slug"]
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.weblog.name} - {self.name}"

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)


class Tag(models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    name_ja = models.CharField(
        max_length=50, blank=True
    )  # Kept for backward compatibility
    slug = models.SlugField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["weblog", "slug"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.weblog.name} - {self.name}"

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)


class Post(models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    title_ja = models.CharField(
        max_length=100, blank=True
    )  # Kept for backward compatibility
    slug = models.SlugField(max_length=100)
    body = models.TextField(blank=True)
    body_ja = models.TextField(blank=True)  # Kept for backward compatibility
    date = models.DateTimeField()
    post_image = models.ImageField(upload_to=f"{UPLOAD_ROOT}/cover_images", blank=True)
    image_url = models.URLField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    is_public = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ["weblog", "slug"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.weblog.name} - {self.title}"

    def get_excerpt(self, language_code="en", length=1000):
        content = self.get_body(language_code)
        soup = BeautifulSoup(content, "html.parser")
        excerpt = ""
        for paragraph in soup.find_all("p"):
            excerpt += f"<p>{paragraph.text}</p>"
            if len(excerpt) >= length:
                break
        return excerpt


class AnonymousCommentUser(models.Model):
    name = models.CharField(max_length=32)
    email = models.CharField(max_length=32, unique=True)
    token = models.CharField(max_length=128, unique=True)
    avatar = models.URLField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create(cls, email, token, avatar=""):
        email_hash = hashlib.md5(email.encode("utf-8")).hexdigest()
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        obj, created = cls.objects.get_or_create(
            email_hash=email_hash, defaults={"token_hash": token_hash, "avatar": avatar}
        )
        return obj

    def __str__(self):
        return f"{self.name} ({self.email[:8]})"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True
    )
    anonymous_user = models.ForeignKey(
        AnonymousCommentUser, on_delete=models.CASCADE, blank=True, null=True
    )
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(blank=True, null=True)
    level = models.IntegerField(default=0)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["post", "created_at"]),
            models.Index(fields=["parent", "created_at"]),
        ]

    def save(self, *args, **kwargs):
        if self.parent:
            self.level = self.parent.level + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.post.title} - {self.body[:50]}..."
