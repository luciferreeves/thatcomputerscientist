import uuid

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from thatcomputerscientist.storage import MinioStorage


class Conversation(models.Model):
    participant_one = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_one",
        verbose_name=_("Participant One"),
    )
    participant_two = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_two",
        verbose_name=_("Participant Two"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated At"))

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("participant_one", "participant_two")
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")

    def __str__(self):
        return f"{self.participant_one.username} & {self.participant_two.username}"

    def get_other_participant(self, user):
        if self.participant_one == user:
            return self.participant_two
        return self.participant_one

    def delete(self, *args, **kwargs):
        for attachment in LetterAttachment.objects.filter(conversation=self):
            attachment.delete()
        super().delete(*args, **kwargs)


class Letter(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="letters",
        verbose_name=_("Conversation"),
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_letters",
        verbose_name=_("Sender"),
    )
    content = models.TextField(verbose_name=_("Content"))
    is_read = models.BooleanField(default=False, verbose_name=pgettext_lazy("letter status", "Read"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Letter")
        verbose_name_plural = _("Letters")

    def __str__(self):
        return f"Letter from {self.sender.username} at {self.created_at}"

    def delete(self, *args, **kwargs):
        for attachment in self.attachments.all():
            attachment.delete()
        super().delete(*args, **kwargs)


def _attachment_upload_path(instance, filename):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    p1 = instance.conversation.participant_one.username
    p2 = instance.conversation.participant_two.username
    return f"letters/{p1}_{p2}/{name}"


class LetterAttachment(models.Model):
    letter = models.ForeignKey(
        Letter,
        on_delete=models.CASCADE,
        related_name="attachments",
        null=True,
        blank=True,
        verbose_name=_("Letter"),
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("Uploader"),
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        verbose_name=_("Conversation"),
    )
    file = models.FileField(
        upload_to=_attachment_upload_path,
        storage=MinioStorage,
        verbose_name=_("File"),
    )
    original_name = models.CharField(max_length=255, verbose_name=_("Original Name"))
    file_size = models.PositiveIntegerField(verbose_name=_("File Size"))
    content_type = models.CharField(max_length=128, verbose_name=_("Content Type"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created At"))

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("Letter Attachment")
        verbose_name_plural = _("Letter Attachments")

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
