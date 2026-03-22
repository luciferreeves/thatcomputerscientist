from __future__ import annotations

from typing import Any

from django.db.models import Model
from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver

from services.journals.models import (
    Character,
    Journal,
    JournalEntry,
    Volume,
)

IMAGE_FIELDS: dict[type[Model], list[str]] = {
    Journal: ["cover_image"],
    JournalEntry: ["thumbnail"],
    Volume: ["cover_image"],
    Character: ["image"],
}


@receiver(pre_delete, sender=Journal)
@receiver(pre_delete, sender=JournalEntry)
@receiver(pre_delete, sender=Volume)
@receiver(pre_delete, sender=Character)
def delete_image_files(sender: type[Model], instance: Model, **kwargs: Any) -> None:
    for field_name in IMAGE_FIELDS.get(sender, []):
        field = getattr(instance, field_name, None)
        if field:
            field.delete(save=False)


@receiver(pre_save, sender=Journal)
@receiver(pre_save, sender=JournalEntry)
@receiver(pre_save, sender=Volume)
@receiver(pre_save, sender=Character)
def cleanup_old_image_files(sender: type[Model], instance: Model, **kwargs: Any) -> None:
    if not instance.pk:
        return
    try:
        old_instance = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return
    for field_name in IMAGE_FIELDS.get(sender, []):
        old_file = getattr(old_instance, field_name, None)
        new_file = getattr(instance, field_name, None)
        if old_file and old_file != new_file:
            old_file.delete(save=False)
