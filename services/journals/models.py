from __future__ import annotations

import re
import uuid
from typing import Any

from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.utils.translation import get_language, gettext_lazy as _
from core.translations import TranslatableMixin, Translation
from services.journals.constants import (
    MODE_CHOICES,
    STATUS_CHOICES,
    GENRE_CHOICES,
    TONE_CHOICES,
    FORM_CHOICES,
    MOOD_CHOICES,
)
from thatcomputerscientist.storage import MinioStorage


def _journal_cover_path(instance: Journal, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"journals/{instance.slug}/cover/{name}"


def _volume_cover_path(instance: Volume, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"journals/{instance.journal.slug}/volumes/{name}"


def _entry_thumbnail_path(instance: JournalEntry, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"journals/{instance.journal.slug}/thumbnails/{name}"


def _character_image_path(instance: Character, filename: str) -> str:
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"journals/{instance.journal.slug}/characters/{name}"


class JournalTranslation(Translation):
    journal = models.ForeignKey(
        "Journal", on_delete=models.CASCADE, related_name="translations"
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        unique_together = ["journal", "language"]

    def __str__(self) -> str:
        return f"{self.journal.name} - {self.get_language_display()}"


class JournalEntryTranslation(Translation):
    journal_entry = models.ForeignKey(
        "JournalEntry", on_delete=models.CASCADE, related_name="translations"
    )
    title = models.CharField(max_length=255)
    content = models.TextField()

    class Meta:
        unique_together = ["journal_entry", "language"]

    def __str__(self) -> str:
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
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="default")
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ongoing", blank=True
    )
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, blank=True)
    cover_image = models.ImageField(
        upload_to=_journal_cover_path, storage=MinioStorage, blank=True
    )
    custom_css = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("owner", "slug")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name

    def get_name(self, language_code: str = "en") -> Any:
        return self.translate("name", language_code)

    @property
    def translated_name(self) -> str:
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.name:
                return translation.name
        except Exception:
            pass
        return self.name

    @property
    def translated_description(self) -> str:
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.description:
                return translation.description
        except Exception:
            pass
        return self.description

    @property
    def entry_label(self) -> str:
        labels: dict[str, Any] = {
            "book": _("Chapter"),
            "light_novel": _("Chapter"),
            "short_stories": _("Story"),
            "poetry": _("Poem"),
            "diary": _("Entry"),
        }
        return str(labels.get(self.mode, _("Entry")))

    @property
    def entry_label_plural(self) -> str:
        labels: dict[str, Any] = {
            "book": _("Chapters"),
            "light_novel": _("Chapters"),
            "short_stories": _("Stories"),
            "poetry": _("Poems"),
            "diary": _("Entries"),
        }
        return str(labels.get(self.mode, _("Entries")))

    def is_accessible_by(self, user: AbstractUser) -> bool:
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
    order = models.PositiveIntegerField(default=0)
    is_draft = models.BooleanField(default=True)
    volume = models.ForeignKey(
        "Volume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
    )
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, blank=True)
    tone = models.CharField(max_length=30, choices=TONE_CHOICES, blank=True)
    form = models.CharField(max_length=30, choices=FORM_CHOICES, blank=True)
    mood = models.CharField(max_length=30, choices=MOOD_CHOICES, blank=True)
    summary = models.TextField(blank=True)
    thumbnail = models.ImageField(
        upload_to=_entry_thumbnail_path, storage=MinioStorage, blank=True
    )
    word_count = models.PositiveIntegerField(default=0)
    entry_date = models.DateField(null=True, blank=True)
    tags = models.ManyToManyField("EntryTag", blank=True, related_name="entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("journal", "slug")
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"

    def _calculate_word_count(self) -> int:
        text = re.sub(r"<[^>]+>", "", self.content)
        return len(text.split())

    @property
    def verse_count(self) -> int:
        blocks = re.findall(r"<p[^>]*>(.*?)</p>", self.content, re.DOTALL)
        return sum(1 for b in blocks if re.sub(r"<[^>]+>", "", b).strip())

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        self.word_count = self._calculate_word_count()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title

    def get_title(self, language_code: str = "en") -> Any:
        return self.translate("title", language_code)

    @property
    def translated_title(self) -> str:
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.title:
                return translation.title
        except Exception:
            pass
        return self.title

    @property
    def translated_content(self) -> str:
        language_code = get_language()
        try:
            translation = self.translations.filter(language=language_code).first()
            if translation and translation.content:
                return translation.content
        except Exception:
            pass
        return self.content


class Volume(models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="volumes"
    )
    title = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(
        upload_to=_volume_cover_path, storage=MinioStorage, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.journal.name} - {self.title}"


class Character(models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="characters"
    )
    name = models.CharField(max_length=255)
    image = models.ImageField(
        upload_to=_character_image_path, storage=MinioStorage, blank=True
    )
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order"]

    def __str__(self) -> str:
        return f"{self.name} ({self.journal.name})"


class CharacterAppearance(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="appearances"
    )
    entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="character_appearances"
    )
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ("character", "entry")

    def __str__(self) -> str:
        return f"{self.character.name} in {self.entry.title}"


class CharacterRelationship(models.Model):
    from_character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="relationships_from"
    )
    to_character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="relationships_to"
    )
    label = models.CharField(max_length=100)

    class Meta:
        unique_together = ("from_character", "to_character")

    def __str__(self) -> str:
        return f"{self.from_character.name} -> {self.to_character.name}: {self.label}"


class EntryTag(models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="entry_tags"
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField()

    class Meta:
        unique_together = ("journal", "slug")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
