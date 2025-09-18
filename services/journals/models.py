from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.translation import get_language
from core.translations import TranslatableMixin, Translation


class JournalTranslation(Translation):
    journal = models.ForeignKey(
        "Journal", on_delete=models.CASCADE, related_name="translations"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["journal", "language"]

    def __str__(self):
        return f"{self.journal.name} - {self.get_language_display()}"


class JournalEntryTranslation(Translation):
    journal_entry = models.ForeignKey(
        "JournalEntry", on_delete=models.CASCADE, related_name="translations"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        unique_together = ["journal_entry", "language"]

    def __str__(self):
        return f"{self.journal_entry.title} - {self.get_language_display()}"


class Journal(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    private = models.BooleanField(default=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journals"
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_journals", blank=True
    )
    custom_css = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("owner", "slug")

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
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

    @property
    def translated_description(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.description:
                return translation.description
        except Exception:
            pass
        return self.description

    def is_accessible_by(self, user):
        if not self.private:
            return True
        if self.owner == user:
            return True
        if user in self.shared_with.all():
            return True
        return False


class JournalEntry(TranslatableMixin, models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="entries"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("journal", "slug")
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_title(self, language_code="en"):
        return self.translate("title", language_code)

    @property
    def translated_title(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.title:
                return translation.title
        except Exception:
            pass
        return self.title

    @property
    def translated_content(self):
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.content:
                return translation.content
        except Exception:
            pass
        return self.content
