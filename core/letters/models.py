import uuid

from django.db import models
from django.conf import settings

from thatcomputerscientist.storage import MinioStorage


class Conversation(models.Model):
    participant_one = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_one",
    )
    participant_two = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="conversations_as_two",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("participant_one", "participant_two")

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
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_letters",
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

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
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
    )
    file = models.FileField(
        upload_to=_attachment_upload_path,
        storage=MinioStorage,
    )
    original_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    content_type = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.original_name

    def delete(self, *args, **kwargs):
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)
