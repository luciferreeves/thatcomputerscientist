from django.db.models.signals import pre_delete
from django.dispatch import receiver

from core.letters.models import LetterAttachment


@receiver(pre_delete, sender=LetterAttachment)
def delete_attachment_file(sender, instance, **kwargs):
    if instance.file:
        instance.file.delete(save=False)
