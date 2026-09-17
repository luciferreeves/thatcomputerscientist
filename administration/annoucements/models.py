from django.conf import settings
from django.db import models
from django.utils import timezone

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
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AnnouncementTranslation(Translation):
    announcement = models.ForeignKey(
        "Announcement", on_delete=models.CASCADE, related_name="translations"
    )
    content = models.TextField()

    class Meta:
        unique_together = ("announcement", "language")


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


class Announcement(TranslatableMixin, models.Model):
    content = models.TextField()
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    is_public = models.BooleanField(default=False)
    is_new = models.BooleanField(default=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.content[:50] + "..." if len(self.content) > 50 else self.content

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = timezone.now()
        return super().save(*args, **kwargs)
