import hashlib
from bs4 import BeautifulSoup
from django.conf import settings
from django.db import models
from django.utils.text import slugify
from django.utils.translation import get_language

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
    @classmethod
    def translate_queryset(cls, queryset, language_code="en"):
        processed_objects = set()
        return [obj.translate(language_code, processed_objects) for obj in queryset]

    def translate(self, language_code="en", processed_objects=None):
        if processed_objects is None:
            processed_objects = set()

        instance_id = f"{self.__class__.__name__}_{self.pk}"
        if instance_id in processed_objects:
            return self

        processed_objects.add(instance_id)
        translation = self.get_translation(language_code)

        if translation:
            translated_fields = [
                field.name
                for field in translation._meta.get_fields()
                if not field.is_relation
                and field.name not in ["id", "language", "created_at", "updated_at"]
            ]

            for field_name in translated_fields:
                translated_value = getattr(translation, field_name, None)
                if translated_value is not None:
                    setattr(self, field_name, translated_value)

        self._translate_relations(language_code, processed_objects)
        return self

    def _translate_relations(self, language_code, processed_objects):
        for field in self._meta.get_fields():
            if not hasattr(field, "related_model") or not hasattr(
                field.related_model, "translate"
            ):
                continue

            if field.one_to_many or field.many_to_many:
                related_manager = getattr(self, field.name, None)
                if related_manager and hasattr(related_manager, "all"):
                    for obj in related_manager.all():
                        obj.translate(language_code, processed_objects)

            elif field.many_to_one or field.one_to_one:
                related_obj = getattr(self, field.name, None)
                if related_obj and hasattr(related_obj, "translate"):
                    related_obj.translate(language_code, processed_objects)

    def get_translation(self, language_code):
        try:
            return self.translations.get(language=language_code)
        except self.translations.model.DoesNotExist:
            return None


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


class Category(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    image = models.URLField(blank=True)
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
        if self.weblog:
            return f"{self.weblog.name} - {self.name}"
        return self.name

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)


class Tag(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    slug = models.SlugField()
    image = models.URLField(blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["weblog", "slug"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.weblog:
            return f"{self.weblog.name} - {self.name}"
        return self.name

    def get_name(self, language_code="en"):
        return self.translate("name", language_code)

    @property
    def translated_name(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.name:
                return translation.name
        except Exception:
            pass
        return self.name


class Post(TranslatableMixin, models.Model):
    weblog = models.ForeignKey(Weblog, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100)
    body = models.TextField(blank=True)
    date = models.DateTimeField()
    post_image = models.ImageField(upload_to=f"{UPLOAD_ROOT}/cover_images", blank=True)
    image_url = models.URLField(blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
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
        if self.weblog:
            return f"{self.weblog.name} - {self.title}"
        return self.title

    def get_excerpt(self, length=1000):
        if not hasattr(self, "_excerpt"):
            soup = BeautifulSoup(self.body, "html.parser")
            excerpt = ""
            for paragraph in soup.find_all("p"):
                p_content = paragraph.decode_contents()
                p_soup = BeautifulSoup(p_content, "html.parser")

                for img in p_soup.find_all("img"):
                    img.decompose()

                if p_soup.get_text().strip():
                    filtered_p = f"<p>{p_soup.decode_contents()}</p>"
                    excerpt += filtered_p

                if len(excerpt) >= length:
                    break
            self._excerpt = excerpt
        return self._excerpt

    @property
    def excerpt(self):
        return self.get_excerpt()

    def get_processed_body(self):
        if not hasattr(self, "_processed_body"):
            soup = BeautifulSoup(self.body, "html.parser")
            first_p = soup.find("p")

            self._first_paragraph = str(first_p) if first_p else ""
            if first_p:
                first_p.decompose()

            self._processed_body = str(soup)

        return self._processed_body

    @property
    def processed_body(self):
        return self.get_processed_body()

    @property
    def first_paragraph(self):
        if not hasattr(self, "_first_paragraph"):
            self.get_processed_body()
        return self._first_paragraph

    def translate(self, language_code="en", processed_objects=None):
        instance = super().translate(language_code, processed_objects)
        if hasattr(instance, "_processed_body"):
            delattr(instance, "_processed_body")
            delattr(instance, "_first_paragraph")
        return instance


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
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
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
