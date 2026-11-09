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
        "Journal", on_delete=models.CASCADE, related_name="translations", verbose_name=_("Journal")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))

    class Meta:
        unique_together = ["journal", "language"]
        verbose_name = _("Journal Translation")
        verbose_name_plural = _("Journal Translations")

    def __str__(self) -> str:
        return f"{self.journal.translated_name} - {self.get_language_display()}"


class JournalEntryTranslation(Translation):
    journal_entry = models.ForeignKey(
        "JournalEntry", on_delete=models.CASCADE, related_name="translations", verbose_name=_("Journal Entry")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    content = models.TextField(verbose_name=_("Content"))

    class Meta:
        unique_together = ["journal_entry", "language"]
        verbose_name = _("Journal Entry Translation")
        verbose_name_plural = _("Journal Entry Translations")

    def __str__(self) -> str:
        return f"{self.journal_entry.translated_title} - {self.get_language_display()}"


class Journal(TranslatableMixin, models.Model):
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    slug = models.SlugField(unique=True, verbose_name=_("Slug"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    private = models.BooleanField(default=False, verbose_name=_("Private"))
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="journals", verbose_name=_("Owner")
    )
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="shared_journals", blank=True, verbose_name=_("Shared With")
    )
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="default", verbose_name=_("Mode"))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="ongoing", blank=True, verbose_name=_("Status")
    )
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, blank=True, verbose_name=_("Genre"))
    cover_image = models.ImageField(
        upload_to=_journal_cover_path, storage=MinioStorage, blank=True, verbose_name=_("Cover Image")
    )
    custom_css = models.TextField(blank=True, verbose_name=_("Custom CSS"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("owner", "slug")
        verbose_name = _("Journal")
        verbose_name_plural = _("Journals")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.translated_name

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
        Journal, on_delete=models.CASCADE, related_name="entries", verbose_name=_("Journal")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(verbose_name=_("Slug"))
    content = models.TextField(verbose_name=_("Content"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    is_draft = models.BooleanField(default=True, verbose_name=_("Draft"))
    volume = models.ForeignKey(
        "Volume",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entries",
        verbose_name=_("Volume"),
    )
    genre = models.CharField(max_length=30, choices=GENRE_CHOICES, blank=True, verbose_name=_("Genre"))
    tone = models.CharField(max_length=30, choices=TONE_CHOICES, blank=True, verbose_name=_("Tone"))
    form = models.CharField(max_length=30, choices=FORM_CHOICES, blank=True, verbose_name=_("Form"))
    mood = models.CharField(max_length=30, choices=MOOD_CHOICES, blank=True, verbose_name=_("Mood"))
    summary = models.TextField(blank=True, verbose_name=_("Summary"))
    thumbnail = models.ImageField(
        upload_to=_entry_thumbnail_path, storage=MinioStorage, blank=True, verbose_name=_("Thumbnail")
    )
    word_count = models.PositiveIntegerField(default=0, verbose_name=_("Word Count"))
    entry_date = models.DateField(null=True, blank=True, verbose_name=_("Entry Date"))
    tags = models.ManyToManyField("EntryTag", blank=True, related_name="entries", verbose_name=_("Tags"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("journal", "slug")
        verbose_name = _("Journal Entry")
        verbose_name_plural = _("Journal Entries")

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
        return self.translated_title

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
        Journal, on_delete=models.CASCADE, related_name="volumes", verbose_name=_("Journal")
    )
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    cover_image = models.ImageField(
        upload_to=_volume_cover_path, storage=MinioStorage, blank=True, verbose_name=_("Cover Image")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ["order"]
        verbose_name = _("Volume")
        verbose_name_plural = _("Volumes")

    def __str__(self) -> str:
        return f"{self.journal.translated_name} - {self.title}"


class Character(models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="characters", verbose_name=_("Journal")
    )
    name = models.CharField(max_length=255, verbose_name=_("Name"))
    image = models.ImageField(
        upload_to=_character_image_path, storage=MinioStorage, blank=True, verbose_name=_("Image")
    )
    bio = models.TextField(blank=True, verbose_name=_("Bio"))
    role = models.CharField(max_length=100, verbose_name=_("Role"))
    order = models.PositiveIntegerField(default=0, verbose_name=_("Order"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ["order"]
        verbose_name = _("Character")
        verbose_name_plural = _("Characters")

    def __str__(self) -> str:
        return f"{self.name} ({self.journal.translated_name})"


class CharacterAppearance(models.Model):
    character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="appearances", verbose_name=_("Character")
    )
    entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="character_appearances", verbose_name=_("Entry")
    )
    notes = models.TextField(blank=True, verbose_name=_("Notes"))

    class Meta:
        unique_together = ("character", "entry")
        verbose_name = _("Character Appearance")
        verbose_name_plural = _("Character Appearances")

    def __str__(self) -> str:
        return f"{self.character.name} in {self.entry.translated_title}"


class CharacterRelationship(models.Model):
    from_character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="relationships_from", verbose_name=_("From Character")
    )
    to_character = models.ForeignKey(
        Character, on_delete=models.CASCADE, related_name="relationships_to", verbose_name=_("To Character")
    )
    label = models.CharField(max_length=100, verbose_name=_("Label"))

    class Meta:
        unique_together = ("from_character", "to_character")
        verbose_name = _("Character Relationship")
        verbose_name_plural = _("Character Relationships")

    def __str__(self) -> str:
        return f"{self.from_character.name} -> {self.to_character.name}: {self.label}"


class EntryTag(models.Model):
    journal = models.ForeignKey(
        Journal, on_delete=models.CASCADE, related_name="entry_tags", verbose_name=_("Journal")
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    slug = models.SlugField(verbose_name=_("Slug"))

    class Meta:
        unique_together = ("journal", "slug")
        verbose_name = _("Entry Tag")
        verbose_name_plural = _("Entry Tags")

    def save(self, *args: Any, **kwargs: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name
